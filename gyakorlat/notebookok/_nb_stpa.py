from _kozos import BETOLTO, code, fejresz, md

NEV = "stpa"
CIM = "STPA: irányítási struktúra, a nem biztonságos beavatkozások lefedettsége és nyomonkövethetősége"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. a sablon elemeiből és kapcsolataiból kirajzolja az irányítási struktúrát (beavatkozás lefelé, visszacsatolás felfelé);
2. lefedettségi mátrixot készít: melyik beavatkozás melyik típusát vizsgálták, és hány nem biztonságos beavatkozás (UCA) született;
3. ellenőrzi a nyomonkövethetőséget: veszteség ← veszély ← UCA ← forgatókönyv ← intézkedés, és jelzi a hiányokat.

A beépített példa a KoboCella cellairányítása (kézikönyv 17. fejezet; Leveson és Thomas, 2018).
""", sablon="stpa_sablon.xlsx", eszkozlap="Gyakorlati útmutató, STPA eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött stpa_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
TIPUSOK = ["nem adja ki", "kiadja", "túl korán / későn / rossz sorrendben", "túl sokáig / túl korán leáll"]
'''),
    md("## Adatok"),
    code('''
def tabla(df, oszlopok):
    df = df.iloc[:, :len(oszlopok)].copy(); df.columns = oszlopok
    return df[df.iloc[:, 0].notna()].reset_index(drop=True)

if SAJAT_SABLON:
    fajl = sablon_betoltese("stpa_sablon.xlsx")
    c = pd.read_excel(fajl, sheet_name="Cél", header=None)
    vesz = tabla(c.iloc[3:13], ["id", "leiras"])
    veszely = tabla(c.iloc[16:26], ["id", "leiras", "L"])
    s = pd.read_excel(fajl, sheet_name="Irányítási struktúra", header=None)
    fej = s.index[s.iloc[:, 0] == "Honnan"][0]
    elemek = tabla(s.iloc[3:fej - 2], ["id", "nev", "tipus", "szint"])
    kapcs = tabla(s.iloc[fej + 1:], ["honnan", "hova", "tipus", "nev"])
    beav = tabla(pd.read_excel(fajl, sheet_name="Beavatkozások", header=None).iloc[3:], ["id", "nev", "iranyito", "cel"])
    uca = tabla(pd.read_excel(fajl, sheet_name="UCA", header=None).iloc[3:], ["id", "ca", "tipus", "leiras", "H"])
    forg = tabla(pd.read_excel(fajl, sheet_name="Forgatókönyvek", header=None).iloc[3:], ["id", "uca", "ok", "leiras", "intezkedes"])
else:
    vesz = pd.DataFrame({"id": ["L1", "L2", "L3"], "leiras": ["a kezelő megsérül", "hibás motor a vevőnél", "termeléskiesés"]})
    veszely = pd.DataFrame({"id": ["H1", "H2", "H3"], "leiras": ["túl nagy sebesség vagy erő a kezelő mellett", "hibás motor elhagyja a cellát", "indokolatlan leállás"], "L": ["L1", "L2", "L3"]})
    elemek = pd.DataFrame({"id": ["MES", "KE", "CV", "BV", "SZ", "FO"],
                           "nev": ["MES", "kezelő", "cellavezérlő", "biztonsági vezérlés", "lézerszkenner", "kobot, csavarozó, befogó"],
                           "tipus": ["irányító", "irányító", "irányító", "irányító", "érzékelő", "szabályozott folyamat"], "szint": [1, 2, 2, 2, 3, 4]})
    kapcs = pd.DataFrame([("MES", "CV", "beavatkozás", "rendelés"), ("CV", "MES", "visszacsatolás", "gyártási adatok"),
                          ("CV", "FO", "beavatkozás", "ciklus indítása"), ("FO", "CV", "visszacsatolás", "nyomaték, állapot"),
                          ("BV", "FO", "beavatkozás", "sebességkorlát, leállítás"), ("BV", "CV", "visszacsatolás", "biztonsági állapot"),
                          ("KE", "CV", "beavatkozás", "nyugtázás, indítás"), ("CV", "KE", "visszacsatolás", "HMI-jelzések"),
                          ("KE", "FO", "beavatkozás", "vészleállítás"), ("FO", "SZ", "visszacsatolás", "a kezelő helyzete"),
                          ("SZ", "BV", "visszacsatolás", "zónajel")], columns=["honnan", "hova", "tipus", "nev"])
    beav = pd.DataFrame({"id": ["CA1", "CA2", "CA3", "CA4"], "nev": ["teljes sebesség engedélyezése", "ciklus indítása", "nyugtázás", "vészleállítás"],
                         "iranyito": ["BV", "CV", "KE", "KE"], "cel": ["FO", "FO", "CV", "FO"]})
    uca = pd.DataFrame([("U1", "CA1", TIPUSOK[1], "", "H1"), ("U2", "CA1", TIPUSOK[2], "", "H1"), ("U3", "CA1", TIPUSOK[3], "", "H1"),
                        ("U4", "CA1", TIPUSOK[0], "", "H3"), ("U5", "CA2", TIPUSOK[1], "", "H2"), ("U6", "CA2", TIPUSOK[2], "", "H1"),
                        ("U7", "CA3", TIPUSOK[1], "", "H2"), ("U8", "CA4", TIPUSOK[0], "", "H1"), ("U9", "CA4", TIPUSOK[2], "", "H1")],
                       columns=["id", "ca", "tipus", "leiras", "H"])
    forg = pd.DataFrame({"id": [f"F{i}" for i in range(1, 9)], "uca": ["U1", "U1", "U2", "U7", "U5", "U8", "U6", "U9"],
                         "ok": ["hibás folyamatmodell", "hiányzó visszacsatolás", "késleltetés", "emberi tényező", "hiányzó visszacsatolás",
                                "elrendezés", "hibás eljárás", "emberi tényező"], "leiras": [""] * 8, "intezkedes": ["x"] * 8})
print(f"{len(vesz)} veszteség, {len(veszely)} veszély, {len(elemek)} elem, {len(kapcs)} kapcsolat, {len(beav)} beavatkozás, {len(uca)} UCA, {len(forg)} forgatókönyv")
'''),
    md("## Lefedettség és nyomonkövethetőség"),
    code('''
lef = pd.crosstab(uca["ca"], uca["tipus"]).reindex(index=beav["id"], columns=TIPUSOK, fill_value=0)
print(lef.to_string())
hiany = []
for h in veszely["id"]:
    if h not in set(uca["H"]):
        hiany.append(f"a(z) {h} veszélyhez nincs UCA")
for u in uca["id"]:
    if u not in set(forg["uca"]):
        hiany.append(f"a(z) {u} UCA-hoz nincs forgatókönyv")
for _, f in forg.iterrows():
    if not str(f["intezkedes"]).strip() or str(f["intezkedes"]) == "nan":
        hiany.append(f"a(z) {f['id']} forgatókönyvhöz nincs intézkedés")
for ca, sor in lef.iterrows():
    nem_vizsgalt = [t for t in TIPUSOK if sor[t] == 0]
    if nem_vizsgalt:
        hiany.append(f"{ca}: UCA nélküli típus(ok): {', '.join(nem_vizsgalt)} (ha nem veszélyes, rögzítsd az indoklást)")
print("\\n".join(hiany) if hiany else "Nincs hiány.")
print("\\nForgatókönyvek ok szerint:", forg["ok"].value_counts().to_dict())
'''),
    md("## Ábra"),
    code('''
G = nx.MultiDiGraph()
for _, e in elemek.iterrows():
    G.add_node(e["id"], nev=e["nev"], szint=int(e["szint"]))
szintek = elemek.groupby("szint")["id"].apply(list).to_dict()
poz = {}
for sz, ids in szintek.items():
    for i, n in enumerate(ids):
        poz[n] = ((i - (len(ids) - 1) / 2) * 3.2, -sz * 1.6)
for n in elemek.loc[elemek["tipus"].isin(["érzékelő", "beavatkozó"]), "id"]:
    poz[n] = (5.0, poz[n][1])          # az érzékelők és beavatkozók oldalra kerülnek, hogy ne takarják a fő ágat
fig, axs = plt.subplots(1, 2, figsize=(15, 5.2), gridspec_kw={"width_ratios": [1.3, 1]})
ax = axs[0]
for _, k in kapcs.iterrows():
    a, b = poz[k["honnan"]], poz[k["hova"]]
    besz = k["tipus"] == "beavatkozás"
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color="#285780" if besz else "#E07B39",
                lw=1.4, ls="-" if besz else "--", shrinkA=22, shrinkB=22, connectionstyle="arc3,rad=" + ("0.12" if besz else "-0.12")))
for n, (x, y) in poz.items():
    tip = elemek.set_index("id").loc[n, "tipus"]
    fc = {"irányító": "#E6EEF6", "érzékelő": "#F1F2F4", "beavatkozó": "#F1F2F4", "szabályozott folyamat": "#285780"}.get(tip, "#E6EEF6")
    ax.text(x, y, G.nodes[n]["nev"], ha="center", va="center", fontsize=8, color="white" if fc == "#285780" else "black",
            bbox=dict(boxstyle="round,pad=0.5", fc=fc, ec="#285780"))
ax.plot([], [], color="#285780", label="beavatkozás"); ax.plot([], [], color="#E07B39", ls="--", label="visszacsatolás")
xs = [v[0] for v in poz.values()]; ys = [v[1] for v in poz.values()]
ax.set_xlim(min(xs) - 2.2, max(xs) + 2.2); ax.set_ylim(min(ys) - 0.9, max(ys) + 0.9)
ax.legend(fontsize=8, loc="lower left"); ax.axis("off")
ax.set_title("Irányítási struktúra", fontsize=10)
ax = axs[1]
im = ax.imshow(lef.to_numpy(), cmap="Oranges", vmin=0, vmax=max(2, lef.to_numpy().max()))
for i in range(lef.shape[0]):
    for j in range(lef.shape[1]):
        v = lef.iat[i, j]
        ax.text(j, i, v if v else "–", ha="center", va="center", fontsize=9)
ax.set_xticks(range(4)); ax.set_xticklabels(["nem adja ki", "kiadja", "időzítés,\\nsorrend", "időtartam"], fontsize=8)
ax.set_yticks(range(len(lef))); ax.set_yticklabels([f"{i} {n}" for i, n in zip(beav["id"], beav["nev"])], fontsize=8)
ax.set_title("UCA-k száma beavatkozásonként és típusonként", fontsize=10)
plt.tight_layout(); plt.savefig("stpa.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A KoboCella négy vizsgált beavatkozásából kilenc nem biztonságos beavatkozás született. A „teljes sebesség engedélyezése” mind a négy típusban veszélyes lehet; a „nyugtázás” csak akkor, ha kiadják (és a hibás darab még nincs a helyén).
- A nyomonkövethetőségi ellenőrzés két UCA-t (U3, U4) mutat forgatókönyv nélkül: ezek a következő elemzési kör feladatai. A „nem veszélyes” típusokat (például a nyugtázás elmaradása) a sablonban indoklással érdemes rögzíteni, hogy látszódjon: a kérdést megvizsgálták.
- A forgatókönyvek okai között a hibás folyamatmodell, a hiányzó visszacsatolás és az emberi tényező egyaránt megjelenik: az STPA ugyanabban a keretben kezeli a szoftver, az érzékelés és az ember hiányosságait.
"""),
]
