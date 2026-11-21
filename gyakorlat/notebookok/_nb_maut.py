from _kozos import BETOLTO, code, fejresz, md

NEV = "maut"
CIM = "Többszempontú hasznosságelemzés (MAUT): nemlineáris hasznosság és súlyozási módszerek"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. szakaszonként lineáris (töréspontos) hasznossági függvényeket rajzol, és rajtuk jelöli az alternatívák értékeit;
2. kiszámítja a rangsor-súlypont (ROC) súlyokat a kritériumok sorrendjéből (Edwards és Barron);
3. négy változatban hasonlítja össze a rangsort: lineáris vagy nemlineáris hasznosság × közvetlen vagy ROC-súlyok, így megmutatja, mennyire függ az eredmény a modellezési döntésektől.

A beépített példa a KoboCella három koncepciója (kézikönyv 10. fejezet).
""", sablon="maut_sablon.xlsx", eszkozlap="Gyakorlati útmutató, MAUT eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött maut_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("maut_sablon.xlsx")
    fv = pd.read_excel(fajl, sheet_name="Függvények", header=3).dropna(subset=["Kód"])
    kodok, nevek = list(fv["Kód"]), list(fv["Kritérium"])
    pontok = {k: [(r[f"x{p}"], r[f"u{p}"]) for p in range(1, 6) if pd.notna(r.get(f"x{p}"))] for k, (_, r) in zip(kodok, fv.iterrows())}
    sw = pd.read_excel(fajl, sheet_name="Súlyok", header=3).iloc[:len(kodok)]
    rang = dict(zip(kodok, sw.iloc[:, 2])); kozvetlen = dict(zip(kodok, sw.iloc[:, 3]))
    ev = pd.read_excel(fajl, sheet_name="Értékelés", header=None)
    alternativak = [a for a in ev.iloc[3, 2:7] if isinstance(a, str)]
    ertek = {k: list(ev.iloc[4 + i, 2:2 + len(alternativak)].astype(float)) for i, k in enumerate(kodok)}
else:
    kodok = ["K1", "K2", "K3", "K4", "K5", "K6"]
    nevek = ["ciklusidő [s]", "utómunka-arány [%]", "törzshajlítás [°]", "beruházás [MFt]", "átállási idő [perc]", "kockázat [pont]"]
    pontok = {"K1": [(45, 10), (55, 9), (65, 7.5), (75, 4), (90, 0)], "K2": [(0.5, 10), (1.0, 8), (2.0, 4), (3.5, 0)],
              "K3": [(10, 10), (20, 7), (30, 2), (45, 0)], "K4": [(0, 10), (60, 7), (90, 3), (120, 0)],
              "K5": [(0, 10), (10, 7), (20, 3), (30, 0)], "K6": [(0, 0), (10, 10)]}
    linearis = {"K1": [(45, 10), (90, 0)], "K2": [(0.5, 10), (3.5, 0)], "K3": [(10, 10), (45, 0)],
                "K4": [(0, 10), (120, 0)], "K5": [(0, 10), (30, 0)], "K6": [(0, 0), (10, 10)]}
    rang = {"K2": 1, "K1": 2, "K3": 3, "K5": 4, "K4": 5, "K6": 6}
    kozvetlen = {"K1": 20, "K2": 20, "K3": 15, "K4": 15, "K5": 15, "K6": 15}
    alternativak = ["A: együttműködő cella", "B: fix állomás", "D: zárt robotcella"]
    ertek = {"K1": [58.6, 52, 48], "K2": [0.8, 0.7, 0.6], "K3": [15, 15, 10], "K4": [78, 95, 110], "K5": [5, 30, 20], "K6": [6, 9, 2]}
if SAJAT_SABLON:   # a lineáris összevetéshez a szélső töréspontokat használjuk
    linearis = {k: [p[0], p[-1]] for k, p in pontok.items()}

def u(pts, x):
    xs, us = zip(*sorted(pts))
    return float(np.interp(x, xs, us))
'''),
    md("## A hasznossági függvények"),
    code('''
szin = ["#285780", "#E07B39", "#3E8E63", "#7D5BA6", "#B83A3A"]
fig, axs = plt.subplots(1, len(kodok), figsize=(2.6 * len(kodok), 2.9), sharey=True)
for ax, k, n in zip(np.atleast_1d(axs), kodok, nevek):
    xs, us = zip(*sorted(pontok[k]))
    ax.plot(xs, us, "-o", color="#4F7FAD", ms=3, label="töréspontos")
    xl, ul = zip(*sorted(linearis[k])); ax.plot(xl, ul, ":", color="#999999", label="lineáris")
    for j, x in enumerate(ertek[k]):
        ax.plot(x, u(pontok[k], x), "s", color=szin[j % 5], ms=6)
    ax.set_title(n, fontsize=9); ax.grid(alpha=0.3); ax.set_ylim(-0.3, 10.5)
np.atleast_1d(axs)[0].set_ylabel("hasznosság (0–10)")
np.atleast_1d(axs)[0].legend(fontsize=7, loc="lower left")
fig.legend([plt.Line2D([], [], marker="s", ls="", color=szin[j % 5]) for j in range(len(alternativak))], alternativak,
           loc="lower center", ncol=len(alternativak), fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.06))
plt.tight_layout(); plt.savefig("maut_fuggvenyek.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("## Súlyok és összevetés"),
    code('''
n = len(kodok)
roc = {k: sum(1 / j for j in range(int(r), n + 1)) / n for k, r in rang.items()}
kozv = {k: v / sum(kozvetlen.values()) for k, v in kozvetlen.items()}
print("ROC-súlyok:", {k: round(roc[k], 3) for k in kodok})

def osszeg(pts_dict, sulyok):
    return np.array([sum(sulyok[k] * u(pts_dict[k], ertek[k][j]) for k in kodok) for j in range(len(alternativak))])

valtozatok = {"lineáris + közvetlen": osszeg(linearis, kozv), "töréspontos + közvetlen": osszeg(pontok, kozv),
              "lineáris + ROC": osszeg(linearis, roc), "töréspontos + ROC": osszeg(pontok, roc)}
t = pd.DataFrame(valtozatok, index=alternativak).round(2)
t.loc["nyertes"] = [alternativak[int(np.argmax(v))].split(":")[0] for v in valtozatok.values()]
t
'''),
    md("""
## Értelmezés

- A töréspontos függvények a követelmények határai körül meredekek (például a ciklusidőnél a 75 s körül, a törzshajlításnál a 20° körül): itt a döntéshozók szerint egy kis javulás is sokat ér.
- A KoboCella példájában a közvetlen súlyokkal mindkét hasznosságmodell az együttműködő cellát (A) hozza ki győztesnek. A ROC-súlyok viszont a sorrend élén álló két kritériumot (utómunka, ciklusidő) erősen felülsúlyozzák, és ezekben a zárt robotcella (D) a legjobb: lineáris hasznossággal a D nyer, töréspontossal az A minimális előnnyel.
- A tanulság: a súlymeghatározás módszere itt nagyobb hatású, mint a hasznossági függvények alakja. Ha a döntéshozók a ROC-súlyokat túlzónak tartják, a közvetlen súlyokat kell egyeztetni velük, és az eltérést a döntési jelentésben dokumentálni.
- Az additív modell feltétele a preferenciafüggetlenség. Ha például a ciklusidő értéke a minőségtől függ (gyors, de selejtes gyártás semmit sem ér), összetettebb aggregálásra vagy kizáró feltételre van szükség.
"""),
]
