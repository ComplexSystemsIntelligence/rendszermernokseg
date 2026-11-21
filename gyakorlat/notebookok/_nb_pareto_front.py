from _kozos import BETOLTO, code, fejresz, md

NEV = "pareto_front"
CIM = "Dominanciavizsgálat és Pareto-front"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook tetszőleges számú cél esetén

1. kiszámítja a dominanciamátrixot (melyik változat melyiket dominálja);
2. azonosítja a nem dominált változatokat, vagyis a közelítő Pareto-frontot, és két cél esetén ábrázolja;
3. korlát esetén megkeresi a korlátot teljesítő nem dominált változatok közül a legjobbat, és kiírja a front mentén az átváltási arányokat (egységnyi javulás ára).

A beépített példa a VárosiBringa tizenkét tervváltozata (kézikönyv 10. fejezet).
""", sablon="pareto_front_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Pareto-front eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött pareto_front_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("pareto_front_sablon.xlsx")
    p = pd.read_excel(fajl, sheet_name="Változatok", header=None)
    celok = [p.iloc[2, 1], p.iloc[4, 1]]; iranyok = [p.iloc[3, 1], p.iloc[5, 1]]
    korlat = p.iloc[6, 1] if pd.notna(p.iloc[6, 1]) else None
    v = p.iloc[10:30, :4].dropna(subset=[0])
    df = pd.DataFrame({"kód": v[0].astype(str), "leírás": v[1], celok[0]: v[2].astype(float), celok[1]: v[3].astype(float)}).reset_index(drop=True)
else:
    celok = ["éves költség [MFt/év]", "elérhetőség [%]"]; iranyok = ["min", "max"]; korlat = 80
    adat = [("V1", 250, 25, 1, 62, 86.0), ("V2", 250, 30, 1, 66, 89.0), ("V3", 300, 25, 1, 68, 88.0), ("V4", 300, 30, 1, 72, 92.0),
            ("V5", 300, 30, 2, 81, 94.5), ("V6", 350, 30, 1, 78, 93.0), ("V7", 350, 35, 1, 83, 95.0), ("V8", 350, 35, 2, 92, 97.0),
            ("V9", 250, 35, 2, 80, 91.0), ("V10", 300, 35, 1, 76, 94.0), ("V11", 350, 25, 2, 85, 92.0), ("V12", 250, 25, 2, 71, 88.5)]
    df = pd.DataFrame([(k, f"{b} kerékpár, {d} dokkoló, {f} furgon", c, e) for k, b, d, f, c, e in adat],
                      columns=["kód", "leírás"] + celok)
X = df[celok].to_numpy(float) * np.array([1 if i == "min" else -1 for i in iranyok])   # minden cél minimalizálandó alakban
'''),
    md("## Dominanciamátrix és nem dominált változatok"),
    code('''
n = len(df)
dom = np.array([[int(i != j and np.all(X[i] <= X[j]) and np.any(X[i] < X[j])) for j in range(n)] for i in range(n)])
df["dominál (db)"] = dom.sum(axis=1)
df["dominálja (db)"] = dom.sum(axis=0)
df["nem dominált"] = df["dominálja (db)"] == 0
for j in np.flatnonzero(~df["nem dominált"].to_numpy()):
    print(f"{df['kód'][j]} dominált; dominálja: {', '.join(df['kód'][np.flatnonzero(dom[:, j])])}")
df
'''),
    md("## A front ábrája, korlát és átváltási arányok"),
    code('''
front = df[df["nem dominált"]].sort_values(celok[0])
fig, ax = plt.subplots(figsize=(8.5, 5))
ax.scatter(df.loc[~df["nem dominált"], celok[0]], df.loc[~df["nem dominált"], celok[1]], s=45, facecolor="#D9D9D9",
           edgecolor="#555555", label="dominált", zorder=3)
ax.plot(front[celok[0]], front[celok[1]], "-o", color="#E07B39", lw=2, ms=7, label="nem dominált (közelítő front)", zorder=4)
for _, r in df.iterrows():
    ax.annotate(r["kód"], (r[celok[0]], r[celok[1]]), xytext=(4, 4), textcoords="offset points", fontsize=8)
if korlat is not None:
    ax.axvline(korlat, color="#285780", ls="--", lw=1.2, label=f"korlát: {korlat}")
ax.set_xlabel(celok[0]); ax.set_ylabel(celok[1]); ax.grid(alpha=0.3); ax.legend(fontsize=8, loc="lower right")
ax.set_title("Tervváltozatok és a közelítő Pareto-front", fontsize=10)
plt.tight_layout(); plt.savefig("pareto_front.png", bbox_inches="tight", dpi=150); plt.show()

if korlat is not None and len(celok) == 2:
    jo = front[front[celok[0]] <= korlat] if iranyok[0] == "min" else front[front[celok[0]] >= korlat]
    legjobb = jo.loc[jo[celok[1]].idxmax()] if iranyok[1] == "max" else jo.loc[jo[celok[1]].idxmin()]
    print(f"A korláton belül a legjobb: {legjobb['kód']} ({legjobb['leírás']}), {celok[1]}: {legjobb[celok[1]]}")
atv = front[["kód"] + celok].copy()
atv["Δ1"] = atv[celok[0]].diff(); atv["Δ2"] = atv[celok[1]].diff()
atv["egységnyi javulás ára (Δ1/Δ2)"] = (atv["Δ1"] / atv["Δ2"]).round(2)
atv
'''),
    md("""
## Értelmezés

- A dominált változatokat súlyok nélkül, nyugodtan elvethetjük: van náluk minden szempontból legalább olyan jó változat.
- A front mentén az **átváltási arány** megmutatja, mennyibe kerül egységnyi javulás. A VárosiBringa példájában a front elején (V1-től V10-ig) egy százalékpont elérhetőség 1,3–2 MFt/évbe kerül, a V10 után már 4–10 MFt/évbe: a javulás egyre drágább, és a V10 egyben a front „könyöke”.
- A front kiválasztott pontja már értékítélet; ezt a döntéshozóknak kell meghozniuk. A korlát (itt a 80 MFt/éves keret) egyszerű és átlátható módja ennek.
- Ha csak néhány változatot vizsgáltunk, a nem dominált változatok csak közelítik a valódi frontot. A teljes tervezési tér frontjának közelítésére többcélú evolúciós algoritmusok valók (kézikönyv 9.8. szakasz).
"""),
]
