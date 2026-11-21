from _kozos import BETOLTO, code, fejresz, md

NEV = "nyomonkovetes"
CIM = "Követelmény-nyomonkövetés gráfként"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook a nyomonkövetési elemekből (elvárások, követelmények, tervelemek, verifikációk) és a szülő–gyerek
kapcsolatokból irányított gráfot épít, és elvégzi a kétirányú nyomonkövethetőség ellenőrzéseit:

1. árva elemek (nincs forrásuk, „aranyozás”?);
2. lebontatlan elvárások és követelmények;
3. **verifikációs lefedettség**: minden követelménynek van-e verifikációja saját magán vagy leszármazottain keresztül;
4. a lánc ábrázolása szintenként.

A beépített példa a KoboCella nyomonkövetési láncának részlete (kézikönyv 6.5. szakasz).
""", sablon="nyomonkovetes_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Nyomonkövethetőség eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött nyomonkovetes_sablon.xlsx „Elemek” és „Kapcsolatok” lapja
''' + BETOLTO + '''
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
ELEMEK = [("EF-01", "elvárás"), ("EF-03", "elvárás"), ("EF-07", "elvárás"),
          ("R-01", "rendszerkövetelmény"), ("R-02", "rendszerkövetelmény"), ("R-05", "rendszerkövetelmény"),
          ("R-09", "rendszerkövetelmény"), ("R-40", "rendszerkövetelmény"),
          ("CS-01", "alrendszer-követelmény"), ("RB-01", "alrendszer-követelmény"),
          ("MA-02", "alrendszer-követelmény"), ("CS-04", "alrendszer-követelmény"),
          ("T-11", "tervelem"), ("T-12", "tervelem"), ("T-13", "tervelem"),
          ("V-01", "verifikáció"), ("V-09", "verifikáció"), ("V-14", "verifikáció")]
KAPCS = [("EF-01", "R-01"), ("EF-01", "R-02"), ("EF-03", "R-05"), ("EF-07", "R-09"),
         ("R-01", "CS-01"), ("R-01", "RB-01"), ("R-05", "MA-02"), ("R-09", "CS-04"),
         ("CS-01", "T-11"), ("CS-04", "T-11"), ("MA-02", "T-12"), ("CS-04", "T-13"),
         ("R-01", "V-01"), ("R-09", "V-09"), ("R-05", "V-14"), ("MA-02", "V-14")]
if SAJAT_SABLON:
    fajl = sablon_betoltese("nyomonkovetes_sablon.xlsx")
    el = pd.read_excel(fajl, sheet_name="Elemek", header=3).dropna(subset=["Azonosító"])
    ka = pd.read_excel(fajl, sheet_name="Kapcsolatok", header=3).dropna(subset=["Szülő azonosító"])
    ELEMEK = list(zip(el["Azonosító"], el["Típus"]))
    KAPCS = list(zip(ka["Szülő azonosító"], ka["Gyerek azonosító"]))
G = nx.DiGraph()
for a, t in ELEMEK:
    G.add_node(a, tipus=t)
G.add_edges_from(KAPCS)
ismeretlen = [n for n in G if "tipus" not in G.nodes[n]]
print("Csomópontok:", G.number_of_nodes(), "· kapcsolatok:", G.number_of_edges(),
      "· ismeretlen azonosító a kapcsolatokban:", ismeretlen or "nincs")
'''),
    md("## Ellenőrzések"),
    code('''
KOV = {"rendszerkövetelmény", "alrendszer-követelmény"}
tipus = nx.get_node_attributes(G, "tipus")
arva = [n for n in G if tipus.get(n) != "elvárás" and G.in_degree(n) == 0]
lebontatlan = [n for n in G if tipus.get(n) in KOV | {"elvárás"} and G.out_degree(n) == 0]
def verifikalt(n):
    return any(tipus.get(d) == "verifikáció" for d in nx.descendants(G, n))
verif_nelkul = [n for n in G if tipus.get(n) in KOV and not verifikalt(n)]
kovek = [n for n in G if tipus.get(n) in KOV]
print("Árva elemek (nincs forrás):", arva)
print("Lebontatlan elvárások / követelmények:", lebontatlan)
print("Verifikáció nélküli követelmények:", verif_nelkul)
print(f"Verifikációs lefedettség: {100 * (1 - len(verif_nelkul) / len(kovek)):.0f}% ({len(kovek) - len(verif_nelkul)}/{len(kovek)})")
'''),
    md("## A nyomonkövetési lánc ábrája"),
    code('''
SZINT = {"elvárás": 0, "rendszerkövetelmény": 1, "alrendszer-követelmény": 2, "tervelem": 3, "verifikáció": 4}
SZIN = {"elvárás": "#F1F2F4", "rendszerkövetelmény": "#E6EEF6", "alrendszer-követelmény": "#E6EEF6",
        "tervelem": "#DDEFE4", "verifikáció": "#ECE5F3"}
for n in G:
    G.nodes[n]["subset"] = SZINT.get(tipus.get(n), 2)
pos = nx.multipartite_layout(G, subset_key="subset", align="vertical")
pos = {n: (x, -y) for n, (x, y) in pos.items()}
fig, ax = plt.subplots(figsize=(12, 6))
gond = set(arva) | set(lebontatlan) | set(verif_nelkul)
nx.draw_networkx_edges(G, pos, ax=ax, arrows=True, arrowsize=12, edge_color="#6B7280", width=1.0)
nx.draw_networkx_nodes(G, pos, ax=ax, node_size=1500,
                       node_color=[SZIN.get(tipus.get(n), "white") for n in G],
                       edgecolors=["#B83A3A" if n in gond else "#285780" for n in G],
                       linewidths=[2.5 if n in gond else 1.0 for n in G])
nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)
for nev, sz in SZINT.items():
    xs = [pos[n][0] for n in G if tipus.get(n) == nev]
    if xs:
        ax.text(xs[0], max(y for _, y in pos.values()) + 0.12, nev, ha="center", fontsize=9, color="#1B3A57")
ax.axis("off"); ax.set_title("Nyomonkövetési lánc (piros keret: ellenőrzési jelzés)")
plt.tight_layout(); plt.savefig("nyomonkovetes.png", bbox_inches="tight"); plt.show()
'''),
    md("""
## Értelmezés

- Az **árva** követelmény (itt R-40, a díszvilágítás) vagy hiányzó forrásra, vagy aranyozásra utal; az utóbbit törölni kell.
- A **lebontatlan** követelmény (R-02, rendelkezésre állás) még nincs alrendszerekre allokálva. A megbízhatósági allokációval a kézikönyv 16. fejezete foglalkozik.
- A **verifikációs lefedettség** a követelmény és leszármazottai között keres verifikációt. A példában az alrendszer-követelményeknek (CS-01, CS-04, RB-01) nincs saját verifikációja. A szülő követelmények ellenőrzése (V-01 ciklusidő-mérés, V-09 adatátadás) közvetve lefedheti őket, de ezt a csapatnak tudatosan kell eldöntenie és dokumentálnia; a beszállítói (alrendszer-szintű) verifikációt gyakran külön kell előírni.
"""),
]
