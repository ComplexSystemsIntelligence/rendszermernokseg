import pathlib
import re

from _kozos import BETOLTO, code, fejresz, md

_FORRAS = (pathlib.Path(__file__).resolve().parent.parent / "sablonok" / "_esemenynaplo_adat.py").read_text(encoding="utf-8")
_GENERATOR = _FORRAS.split('if __name__ == "__main__":')[0]
_GENERATOR = re.sub(r'^""".*?"""\n', "", _GENERATOR, count=1, flags=re.S)

NEV = "folyamatbanyaszat"
CIM = "Folyamatbányászat alapjai: eseménynapló, változatok, közvetlen követési gráf, megfelelőség és teljesítmény"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. betölti vagy előállítja az eseménynaplót, és ellenőrzi az adatminőséget;
2. feltárja a folyamatváltozatokat és a közvetlen követési gráfot (gyakoriságokkal és átlagos várakozási időkkel);
3. a folyamatmodell megengedett követéseivel összevetve megkeresi az eltérő eseteket (megfelelőség-ellenőrzés);
4. a teljesítményt esetcsoportonként elemzi, és az erőforrás-nézőpontból kimutatja, mely rendeléseket előzték meg az átsorolt rendelések.

A beépített példa a ForgácsTech MES-ének szimulált eseménynaplója az első három hónapból, 300 rendeléssel (kézikönyv 20. és 25. fejezet; van der Aalst, 2016). A teljes eszköztárhoz (például induktív bányászó algoritmus, tokenalapú visszajátszás) a `pm4py` könyvtár ajánlott (Berti és mtsai, 2019).
""", sablon="folyamatbanyaszat_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Folyamatbányászat alapjai eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött folyamatbanyaszat_sablon.xlsx (Napló és Esetek lap)
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
'''),
    md("## Az eseménynapló"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("folyamatbanyaszat_sablon.xlsx")
    naplo = pd.read_excel(fajl, sheet_name="Napló", header=3).iloc[:, :5]
    naplo.columns = ["eset", "tev", "kezd", "bef", "eroforras"]
    naplo = naplo[naplo.eset.notna()].copy()
    esetek = pd.read_excel(fajl, sheet_name="Esetek", header=3).iloc[:, :4]
    esetek.columns = ["eset", "rendeles", "hatarido", "gep"]
    esetek = esetek[esetek.eset.notna()].copy()
    modell = pd.read_excel(fajl, sheet_name="Modell", header=3).iloc[:, :2].dropna()
    MODELL = set(map(tuple, modell.to_numpy()))
else:
''' + "\n".join("    " + sor if sor.strip() else "" for sor in _GENERATOR.splitlines()) + '''
    naplo = pd.DataFrame(NAPLO, columns=["eset", "tev", "kezd", "bef", "eroforras"])
    esetek = pd.DataFrame(ESETEK, columns=["eset", "rendeles", "hatarido", "gep"])
    MODELL = set(MODELL_KOVETESEK) | {("Kiszállítás", "(vége)")}
for c in ("kezd", "bef"):
    naplo[c] = pd.to_datetime(naplo[c])
naplo = naplo.sort_values(["eset", "kezd"]).reset_index(drop=True)
print(f"{naplo.eset.nunique()} eset, {len(naplo)} esemény, {naplo.tev.nunique()} tevékenység")
print(naplo.head(9).to_string(index=False))
'''),
    md("""## Adatminőség

A folyamatbányászat eredménye a napló minőségén múlik: hiányzó vagy rossz sorrendű időbélyegek, eltérő tevékenységnevek és rosszul meghatározott esetfogalom torz modellt adnak (van der Aalst, 2016)."""),
    code('''
hiany = naplo[["eset", "tev", "kezd"]].isna().sum().sum()
rossz = int((naplo.bef < naplo.kezd).sum())
print(f"Hiányzó kötelező érték: {hiany}; befejezés a kezdés előtt: {rossz}")
print("Tevékenységek gyakorisága:"); print(naplo.tev.value_counts().to_string())
esemeny_eset = naplo.groupby("eset").size()
print(f"\\nEsemények esetenként: átlag {esemeny_eset.mean():.1f}, min {esemeny_eset.min()}, max {esemeny_eset.max()}")
'''),
    md("## Folyamatváltozatok"),
    code('''
nyomok = naplo.groupby("eset").tev.apply(tuple)
valt = nyomok.value_counts()
print(f"{len(valt)} változat; a leggyakoribbak:")
for v, db in valt.head(6).items():
    print(f"  {db:4d} ({db / len(nyomok):5.1%})  {' → '.join(v)}")
'''),
    md("""## Közvetlen követési gráf

Két tevékenység között akkor van él, ha egy esetben az egyik közvetlenül a másik után következik; az él címkéje a gyakoriság és az átlagos várakozás (az első befejezésétől a második kezdetéig)."""),
    code('''
naplo["kov"] = naplo.groupby("eset").tev.shift(-1).fillna("(vége)")
naplo["kov_kezd"] = naplo.groupby("eset").kezd.shift(-1)
naplo["var_h"] = (naplo.kov_kezd - naplo.bef).dt.total_seconds() / 3600
dfg = naplo.groupby(["tev", "kov"]).agg(db=("eset", "size"), var_h=("var_h", "mean")).reset_index()
dfg["modellben"] = [(a, b) in MODELL for a, b in zip(dfg.tev, dfg.kov)]
print(dfg.sort_values("db", ascending=False).round(1).to_string(index=False))
'''),
    md("""## Megfelelőség a modellel

Egyszerű megfelelőség-ellenőrzés: egy eset akkor tér el a modelltől, ha van olyan közvetlen követése, amelyet a modell nem enged meg. Az eset illeszkedése a megengedett követések aránya. (A tokenalapú visszajátszás és az igazítás ennél pontosabb módszer; lásd `pm4py`.)"""),
    code('''
naplo["ok"] = [(a, b) in MODELL for a, b in zip(naplo.tev, naplo.kov)]
illesz = naplo.groupby("eset").ok.mean()
elter = illesz[illesz < 1].index
print(f"A modelltől eltérő esetek: {len(elter)} ({len(elter) / naplo.eset.nunique():.1%}); átlagos illeszkedés {illesz.mean():.3f}")
print("A modellben nem szereplő követések:")
print(dfg[~dfg.modellben].sort_values("db", ascending=False)[["tev", "kov", "db"]].to_string(index=False))
'''),
    md("""## Teljesítmény és erőforrás-nézőpont

Az átsorolt rendelés a gép sorában előre kerül. Megelőzöttnek tekintjük azt a nem átsorolt rendelést, amelyet ugyanazon a gépen egy később ütemezett, de átsorolt rendelés előbb került megmunkálásra."""),
    code('''
esetek = esetek.set_index("eset")
for c in ("rendeles", "hatarido"):
    esetek[c] = pd.to_datetime(esetek[c])
esetek["vege"] = naplo.groupby("eset").bef.max()
esetek["atfutas"] = (esetek.vege - esetek.rendeles).dt.total_seconds() / 86400
esetek["keso"] = esetek.vege > esetek.hatarido
atsor = set(naplo.loc[naplo.tev == "Rendelés átsorolása", "eset"])
utem = naplo[naplo.tev == "Ütemezés"].set_index("eset").kezd
megm = naplo[naplo.tev == "Megmunkálás"].set_index("eset")
esetek["utem"], esetek["mkezd"], esetek["gepen"] = utem, megm.kezd, megm.eroforras
megelozott, kesleltetes = set(), []
for g, grp in esetek.groupby("gepen"):
    for o, x in grp.iterrows():
        if o in atsor: continue
        m = grp.index.isin(list(atsor)) & (grp.utem > x.utem) & (grp.mkezd < x.mkezd)
        if m.any():
            megelozott.add(o)
            kesleltetes.append(((megm.loc[grp.index[m], "bef"] - megm.loc[grp.index[m], "kezd"]).dt.total_seconds() / 86400).sum())
esetek["csoport"] = np.where(esetek.index.isin(list(atsor)), "átsorolt", np.where(esetek.index.isin(list(megelozott)), "megelőzött", "egyéb"))
T = esetek.groupby("csoport").agg(esetek=("atfutas", "size"), atfutas_nap=("atfutas", "mean"), hataridore=("keso", lambda s: 1 - s.mean()))
print(T.round(3).to_string())
print(f"\\nHatáridőre összesen: {1 - esetek.keso.mean():.1%}; a megelőzött rendeléseket átlagosan {np.mean(kesleltetes):.1f} munkanapnyi "
      "átsorolt megmunkálás előzte meg")
'''),
    md("## Ábra"),
    code('''
fig, ax = plt.subplots(1, 2, figsize=(16, 6.5), gridspec_kw={"width_ratios": [1.6, 1]})
G = nx.DiGraph()
for r in dfg.itertuples():
    G.add_edge(r.tev, r.kov, db=r.db, var=r.var_h, ok=r.modellben)
atl = naplo.assign(i=naplo.groupby("eset").cumcount()).groupby("tev").i.mean()
atl["(vége)"] = atl.max() + 1
sor = sorted(G.nodes, key=lambda n: atl.get(n, 0))
OLDAL = {"Rendelés átsorolása": ("Ütemezés", 1.2), "Utómunka": ("Mérés", -1.2)}   # a fő ágon kívüli csomópontok
fo = [n for n in sor if n not in OLDAL]
pos = {n: (float(k), 0.0) for k, n in enumerate(fo)}
for n, (szomszed, y) in OLDAL.items():
    if n in G.nodes:
        pos[n] = (pos.get(szomszed, (0.0, 0.0))[0] + 0.5, y)
nx.draw_networkx_nodes(G, pos, ax=ax[0], node_size=2300, node_color="#E6EEF6", edgecolors="#285780")
nx.draw_networkx_labels(G, pos, ax=ax[0], labels={n: n.replace(" ", "\\n", 1).replace("Visszaigazolás", "Vissza-\\nigazolás").replace("Megmunkálás", "Megmun-\\nkálás") for n in G.nodes}, font_size=7)
for u, v, d in G.edges(data=True):
    dx, dy = pos[v][0] - pos[u][0], pos[v][1] - pos[u][1]
    rad = 0.35 if dx < 0 else (0.45 if (dx > 1 and dy == 0) else 0.0)
    nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], ax=ax[0], width=0.6 + 3.0 * d["db"] / dfg.db.max(),
                           edge_color="#285780" if d["ok"] else "#B83A3A", arrowsize=14, node_size=2300,
                           connectionstyle=f"arc3,rad={rad}")
    xm, ym = (pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2 + (-0.42 if rad == 0.45 else (0.28 if rad else 0.12))
    ax[0].text(xm, ym, f"{d['db']}", fontsize=7, ha="center", color="#B83A3A" if not d["ok"] else "#1F2933")
ax[0].set_title("Közvetlen követési gráf (piros: a modellben nem szereplő követés; címke: esetek száma)", fontsize=10)
ax[0].axis("off")

cs = ["egyéb", "megelőzött", "átsorolt"]
ax[1].bar(cs, [T.loc[c, "atfutas_nap"] if c in T.index else 0 for c in cs], color=["#A9C4DE", "#B83A3A", "#285780"])
for k, c in enumerate(cs):
    if c in T.index:
        ax[1].text(k, T.loc[c, "atfutas_nap"] + 0.2, f"{T.loc[c, 'hataridore']:.0%} határidőre", ha="center", fontsize=9)
ax[1].set_ylabel("átlagos átfutás [nap]"); ax[1].set_title("Átfutás esetcsoportonként")
ax[1].spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig("folyamatbanyaszat.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""## Értelmezés

- Az adatminőség rendben van; a napló a valós működést mutatja.
- Az esetek kb. 17%-ában szerepel a modellben nem szereplő „rendelés átsorolása” lépés, néhány esetben pedig kimarad a mérés; a modelltől eltérő esetek aránya kb. 20%.
- Az átsorolt rendelések mind határidőre teljesülnek, de a megelőzött rendelések átfutása lényegesen hosszabb, és több mint harmaduk késik: az átsorolás nem szünteti meg a késést, csak áthelyezi.
- A következmény a modellre és a szabályokra vonatkozik: az átsorolás bekerült a modellbe, és csak akkor engedélyezett, ha a megelőzött rendelések határideje így is tartható (kézikönyv 20. fejezet).
"""),
]
