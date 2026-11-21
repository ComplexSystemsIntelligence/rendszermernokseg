from _kozos import BETOLTO, code, fejresz, md

NEV = "sorkiegyenlites"
CIM = "Ütemidő és sorkiegyenlítés: sorrendi gráf, Yamazumi-diagram, rangsorolt pozíciós súly heurisztika, kezelők terhelése"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. kiszámítja az ütemidőt és a berendezéshatékonysággal csökkentett ciklusidő-korlátot;
2. ellenőrzi a jelenlegi hozzárendelést: állomásidők, sorrendi kötöttségek, kiegyenlítési hatásfok, Yamazumi-diagram;
3. a rangsorolt pozíciós súly (RPW) heurisztikával új hozzárendelést javasol a korlátra és az ütemidőre; a gépi műveleteket a megelőző kézi művelettel együtt kezeli (ugyanazon a berendezésen futnak);
4. összeveti a kezelők kézi terhelését a jelenlegi és egy összevont kezelői beosztásnál.

A beépített példa a KoboCella ötállomásos motorszerelő sora (kézikönyv 19. fejezet). A heurisztikát Helgeson és Birnie (1961) javasolta; a sorkiegyenlítési módszerek áttekintése: Scholl és Becker (2006).
""", sablon="sorkiegyenlites_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Ütemidő és sorkiegyenlítés eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött sorkiegyenlites_sablon.xlsx
OSSZEVONAS = {"K5": "K3"}   # kezelői változat: K5 feladatait K3 veszi át
''' + BETOLTO + '''
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
'''),
    md("## Adatok és ütemidő"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("sorkiegyenlites_sablon.xlsx")
    p = pd.read_excel(fajl, sheet_name="Műveletek", header=None, nrows=5)
    IDO_ORA, KERESLET, OEE = float(p.iloc[2, 1]), float(p.iloc[3, 1]), float(p.iloc[4, 1])
    m = pd.read_excel(fajl, sheet_name="Műveletek", header=8).iloc[:, :8]
    m.columns = ["id", "nev", "t", "tipus", "e1", "e2", "allomas", "kezelo"]
    m = m[m.id.notna() & m.t.notna()].reset_index(drop=True)
else:
    IDO_ORA, KERESLET, OEE = 3450, 140000, 0.85
    m = pd.DataFrame([
        ("E1", "állórész behelyezése", 12, "kézi", None, None, 1, "K1"), ("E2", "tekercsvégek bekötése", 34, "kézi", "E1", None, 1, "K1"),
        ("E3", "csatlakozó beültetése", 24, "kézi", "E2", None, 1, "K1"), ("E4", "csapágy felsajtolása", 20, "kézi", None, None, 2, "K2"),
        ("E5", "rotor behelyezése", 24, "kézi", "E3", "E4", 2, "K2"), ("E6", "hátsó pajzs", 18, "kézi", "E5", None, 2, "K2"),
        ("E7", "KoboCella: behelyezés", 18, "kézi", "E6", None, 3, "K3"), ("E8", "KoboCella: csavarozás (kobot)", 56.1, "gépi", "E7", None, 3, None),
        ("E9", "tesztbe helyezés", 12, "kézi", "E8", None, 4, "K4"), ("E10", "elektromos teszt", 60, "gépi", "E9", None, 4, None),
        ("E11", "címkézés", 10, "kézi", "E10", None, 5, "K5"), ("E12", "csomagolás", 25, "kézi", "E11", None, 5, "K5")],
        columns=["id", "nev", "t", "tipus", "e1", "e2", "allomas", "kezelo"])
m["t"] = m.t.astype(float)
m["allomas"] = pd.to_numeric(m.allomas, errors="coerce").fillna(0).astype(int)
TT = IDO_ORA * 3600 / KERESLET
KORLAT = TT * OEE
munkatartalom = m.t.sum()
print(f"Ütemidő {TT:.1f} s; ciklusidő-korlát (OEE {OEE:.0%}) {KORLAT:.1f} s; munkatartalom {munkatartalom:.1f} s")
print(f"Elméleti minimum: {math.ceil(munkatartalom / TT)} állomás az ütemidőre, {math.ceil(munkatartalom / KORLAT)} a korlátra")

G = nx.DiGraph()
for _, r in m.iterrows():
    G.add_node(r.id, t=r.t, tipus=r.tipus)
    for e in (r.e1, r.e2):
        if isinstance(e, str) and e.strip():
            G.add_edge(e.strip(), r.id)
assert nx.is_directed_acyclic_graph(G), "A sorrendi kötöttségek kört tartalmaznak!"
'''),
    md("## A jelenlegi hozzárendelés"),
    code('''
all_ = m.groupby("allomas").agg(kezi=("t", lambda s: s[m.loc[s.index, "tipus"] == "kézi"].sum()),
                                 gepi=("t", lambda s: s[m.loc[s.index, "tipus"] == "gépi"].sum()))
all_["ido"] = all_.kezi + all_.gepi
c = all_.ido.max()
allomas_of = dict(zip(m.id, m.allomas))
sertes = [(u, v) for u, v in G.edges if allomas_of[u] > allomas_of[v]]
print(all_.round(1).to_string())
print(f"Szűk keresztmetszet: {all_.ido.idxmax()}. állomás ({c:.1f} s); kapacitás {3600 / c:.1f} db/óra, igény {3600 / TT:.1f} db/óra; "
      f"hatásfok {munkatartalom / (len(all_) * c):.1%}; a korlátot túllépő állomás: {int((all_.ido > KORLAT).sum())}; sorrendi sértés: {sertes or 'nincs'}")
'''),
    md("## Rangsorolt pozíciós súly (RPW) heurisztika"),
    code('''
# A gépi műveletet a közvetlen megelőzőjével egy blokkba vonjuk: ugyanazon a berendezésen fut.
blokk = {n: n for n in G.nodes}
for _, r in m.iterrows():
    if r.tipus == "gépi" and isinstance(r.e1, str):
        blokk[r.id] = blokk[r.e1.strip()]
B = nx.DiGraph()
for n in G.nodes:
    B.add_node(blokk[n])
for b in B.nodes:
    B.nodes[b]["t"] = sum(G.nodes[n]["t"] for n in G.nodes if blokk[n] == b)
    B.nodes[b]["tagok"] = [n for n in G.nodes if blokk[n] == b]
for u, v in G.edges:
    if blokk[u] != blokk[v]:
        B.add_edge(blokk[u], blokk[v])

def rpw(B, c):
    suly = {b: B.nodes[b]["t"] + sum(B.nodes[d]["t"] for d in nx.descendants(B, b)) for b in B.nodes}
    kiosztott, allomasok = set(), []
    while len(kiosztott) < len(B):
        akt, ido = [], 0.0
        while True:
            jelolt = [b for b in B.nodes if b not in kiosztott and all(p in kiosztott for p in B.predecessors(b))
                      and ido + B.nodes[b]["t"] <= c + 1e-9]
            if not jelolt:
                break
            b = max(jelolt, key=lambda x: suly[x])
            akt.append(b); kiosztott.add(b); ido += B.nodes[b]["t"]
        if not akt:   # egy blokk önmagában nagyobb a ciklusidőnél
            b = next(b for b in B.nodes if b not in kiosztott and all(p in kiosztott for p in B.predecessors(b)))
            akt, ido = [b], B.nodes[b]["t"]; kiosztott.add(b)
        allomasok.append((akt, ido))
    return allomasok

for cel, c_ in (("korlát", KORLAT), ("ütemidő", TT)):
    a = rpw(B, c_)
    cmax = max(i for _, i in a)
    print(f"RPW, cél: {cel} ({c_:.1f} s): {len(a)} állomás, c = {cmax:.1f} s, hatásfok {munkatartalom / (len(a) * cmax):.1%}")
    for k, (bl, ido) in enumerate(a, 1):
        tagok = sum((B.nodes[b]["tagok"] for b in bl), [])
        print(f"   {k}. állomás: {', '.join(tagok)}  ({ido:.1f} s)")
'''),
    md("## A kezelők terhelése"),
    code('''
kezi = m[m.tipus == "kézi"]
terh = kezi.groupby("kezelo").t.sum()
valt = kezi.assign(kezelo=kezi.kezelo.replace(OSSZEVONAS)).groupby("kezelo").t.sum()
CT_sor = max(TT, c)
for nev, t in (("jelenlegi", terh), ("változat", valt)):
    print(f"{nev}: {len(t)} kezelő, terhelés: {', '.join(f'{k} {v:.0f} s ({v / TT:.0%})' for k, v in t.items())}; "
          f"munkaerő-kihasználtság {kezi.t.sum() / (len(t) * CT_sor):.1%}")
# mohó javaslat: a két legkisebb terhelésű kezelő összevonása, amíg az összeg a korlát 80%-a alatt marad
t = terh.to_dict(); javaslat = []
while len(t) > 1:
    a, b = sorted(t, key=t.get)[:2]
    if t[a] + t[b] > 0.8 * KORLAT:
        break
    t[a + "+" + b] = t.pop(a) + t.pop(b); javaslat.append(a + "+" + b)
print("Mohó összevonási javaslat (legfeljebb a korlát 80%-áig):", javaslat or "nincs", "→", len(t), "kezelő")
'''),
    md("## Ábra"),
    code('''
fig, axs = plt.subplots(1, 3, figsize=(17, 4.8), gridspec_kw={"width_ratios": [1.3, 1, 1]})
ax = axs[0]
# késői (ALAP) rétegezés: minden művelet a lehető legközelebb kerül az utódjához
hossz = {}
for n in reversed(list(nx.topological_sort(G))):
    hossz[n] = max((hossz[s] + 1 for s in G.successors(n)), default=0)
hmax = max(hossz.values())
mely = {}
for n in nx.topological_sort(G):
    mely[n] = max((mely[p] + 1 for p in G.predecessors(n)), default=0)
szint, pos = {}, {}
for n in sorted(G.nodes, key=lambda n: (hmax - hossz[n], -mely[n])):
    k = hmax - hossz[n]; szint[k] = szint.get(k, 0) + 1
    pos[n] = (k, -0.8 * (szint[k] - 1))
szinek = ["#E07B39" if G.nodes[n]["tipus"] == "gépi" else "#A9C4DE" for n in G.nodes]
nx.draw_networkx(G, pos, ax=ax, node_color=szinek, node_size=650, font_size=8, arrowsize=12, edge_color="#7A8C9E")
for n, (x, y) in pos.items():
    ax.text(x, y - 0.25, f"{G.nodes[n]['t']:g} s", ha="center", fontsize=7)
ax.set_title("Sorrendi gráf (narancs: gépi művelet)", fontsize=10); ax.axis("off")
ax.set_ylim(min(y for _, y in pos.values()) - 0.5, 0.4)
ax = axs[1]
x = np.arange(len(all_))
ax.bar(x, all_.kezi, color="#285780", label="kézi")
ax.bar(x, all_.gepi, bottom=all_.kezi, color="#E07B39", label="gépi")
ax.axhline(TT, color="#B83A3A", ls="--", label=f"ütemidő {TT:.1f} s")
ax.axhline(KORLAT, color="#6B4C9A", ls=":", label=f"korlát {KORLAT:.1f} s")
for i, v in enumerate(all_.ido):
    ax.text(i, v + 1, f"{v:.1f}", ha="center", fontsize=8)
ax.set_xticks(x, [f"{i}." for i in all_.index]); ax.set_xlabel("állomás"); ax.set_ylabel("idő [s]")
ax.set_ylim(0, TT * 1.2); ax.legend(fontsize=8, loc="upper right"); ax.set_title("Yamazumi-diagram", fontsize=10)
ax = axs[2]
osszes = sorted(set(terh.index) | set(valt.index))
x = np.arange(len(osszes))
ax.bar(x - 0.2, [terh.get(k, 0) for k in osszes], 0.4, color="#285780", label="jelenlegi")
ax.bar(x + 0.2, [valt.get(k, 0) for k in osszes], 0.4, color="#3E8E63", label="összevont változat")
ax.axhline(TT, color="#B83A3A", ls="--"); ax.text(-0.4, TT + 1, "ütemidő", fontsize=8, color="#B83A3A")
ax.set_xticks(x, osszes); ax.set_ylabel("kézi munka [s/ütem]"); ax.legend(fontsize=8, loc="upper right")
ax.set_ylim(0, TT * 1.2); ax.set_title("A kezelők kézi terhelése", fontsize=10)
plt.tight_layout(); plt.savefig("sorkiegyenlites.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- Az ütemidő 88,7 s, a 85%-os berendezéshatékonyságra tervezett ciklusidő-korlát 75,4 s. A munkatartalom 313,1 s, így az ütemidőre elméletileg 4, a korlátra 5 állomás kell.
- A jelenlegi öt állomás mindegyike a korlát alatt van; a szűk keresztmetszet a KoboCella (74,1 s), a hatásfok 84,5%.
- Az RPW heurisztika a korlátra és az ütemidőre is öt állomást ad: a négyállomásos elméleti minimumot a sorrendi kötöttségek és a berendezésekhez kötött, nem osztható gépi műveletek (a kobot és a tesztberendezés) nem engedik elérni. Ütemidőre számolva a címkézés a teszthez kerülhet.
- A létszám ezért nem az állomások összevonásával, hanem a kezelői feladatok összevonásával csökkenthető: ha a KoboCella kezelője átveszi a címkézést és a csomagolást, terhelése 53 s (az ütemidő 60%-a), a kezelők száma négy, a munkaerő-kihasználtság 44%-ról 56%-ra nő. A mohó összevonás a teszt kezelőjét vonná össze a KoboCella kezelőjével (30 s); a csapat a csomagolást választotta, mert a csomagolóasztal a cella kiadóoldalára tehető. A változtatás előtt az elrendezést és a kezelő terhelését is ellenőrizni kell.
"""),
]
