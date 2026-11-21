from _kozos import BETOLTO, code, fejresz, md

NEV = "pha"
CIM = "Előzetes veszélyelemzés (PHA): kockázatcsökkentés veszélyenként és az intézkedések minősége"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. beolvassa a PHA-sablon veszélyeit, és kiszámítja a kiinduló és a maradó kockázati zónát;
2. veszélyenként ábrázolja a kockázatcsökkentést, az intézkedés típusával (ISO 12100: tervezés, műszaki védőintézkedés, tájékoztatás);
3. jelzi a hiányosságokat: elfogadhatatlan maradó kockázat, indoklás nélküli ALARP, súlyos veszély csak tájékoztatással kezelve, hiányzó verifikáció;
4. összesíti a veszélyeket energiaforrásonként.

A beépített példa a KoboCella előzetes veszélyelemzése (kézikönyv 14. fejezet).
""", sablon="pha_sablon.xlsx", eszkozlap="Gyakorlati útmutató, PHA eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött pha_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
TIPUS = {1: "eredendően biztonságos tervezés", 2: "műszaki védőintézkedés", 3: "használati információ"}
'''),
    md("## Adatok"),
    code('''
OSZL = ["id", "alrendszer", "energia", "veszely", "ok", "celpont", "kovetkezmeny", "S0", "P0", "z0", "intezkedes", "tipus",
        "S1", "P1", "z1", "indoklas", "verifikacio", "jelzes"]
if SAJAT_SABLON:
    fajl = sablon_betoltese("pha_sablon.xlsx")
    sk = pd.read_excel(fajl, sheet_name="Skálák", header=None)
    PIROS, NARANCS = int(sk.iloc[11, 3]), int(sk.iloc[12, 3])
    pha = pd.read_excel(fajl, sheet_name="PHA", header=3).iloc[:, :18]
    pha.columns = OSZL
    pha = pha[pha["veszely"].notna() & pha["S0"].notna()]
else:
    PIROS, NARANCS = 8, 6
    sorok = [
        ("H1", "kobot", "mozgási (mechanikai)", "a kobotkar ütközése a kezelővel", 3, 4, 2, 2, 3, "", "erőmérés"),
        ("H2", "befogó", "nyomás, rugalmas", "kéz becsípődése a befogóban", 4, 3, 1, 3, 2, "", "erőmérés"),
        ("H3", "csavarozó egység", "mozgási (mechanikai)", "behúzás a forgó orsóba", 3, 3, 2, 3, 1, "", "funkcionális teszt"),
        ("H4", "vezérlőszekrény", "villamos", "áramütés", 5, 2, 2, 5, 1, "a súlyosság nem csökkenthető; a további csökkentés aránytalan", "audit"),
        ("H5", "munkahely", "ergonómiai terhelés", "ismétlődő törzshajlítás", 3, 5, 1, 2, 3, "", "ergonómiai mérés"),
        ("H6", "cellavezérlés", "vezérlés, szoftver", "váratlan indulás", 4, 2, 1, 4, 1, "", "validálás"),
        ("H7", "anyagellátás", "helyzeti (gravitációs)", "leeső motorház", 2, 3, 3, 2, 2, "", "bejárás"),
        ("H8", "befogó pneumatika", "nyomás, rugalmas", "levegőtömlő leválása", 3, 2, 2, 3, 1, "", "nyomáspróba"),
    ]
    pha = pd.DataFrame(sorok, columns=["id", "alrendszer", "energia", "veszely", "S0", "P0", "tipus", "S1", "P1", "indoklas", "verifikacio"])
for c in ("S0", "P0", "S1", "P1", "tipus"):
    pha[c] = pd.to_numeric(pha[c], errors="coerce").astype("Int64")
pha["indoklas"] = pha["indoklas"].fillna("").astype(str); pha["verifikacio"] = pha["verifikacio"].fillna("").astype(str)

def zona(s, p):
    return "elfogadhatatlan" if s + p >= PIROS else ("ALARP" if s + p >= NARANCS else "elfogadható")
pha["z0"] = [zona(s, p) for s, p in zip(pha.S0, pha.P0)]
pha["z1"] = [zona(s, p) for s, p in zip(pha.S1, pha.P1)]
print(f"{len(pha)} veszély, {pha['energia'].nunique()} energiafajta")
'''),
    md("## Ellenőrzések"),
    code('''
def jelzes(r):
    if r.z1 == "elfogadhatatlan":
        return "további intézkedés kell"
    if r.z1 == "ALARP" and not r.indoklas.strip():
        return "ALARP-indoklás hiányzik"
    if r.S0 >= 4 and r.tipus == 3:
        return "súlyos veszélynél a tájékoztatás nem elég"
    if not r.verifikacio.strip():
        return "verifikáció hiányzik"
    return ""
pha["jelzes"] = pha.apply(jelzes, axis=1)
hiany = pha[pha.jelzes != ""]
print(hiany[["id", "veszely", "jelzes"]].to_string(index=False) if len(hiany) else "Nincs hiányosság.")
print()
print("Zónák (kiinduló -> maradó):")
print(pd.crosstab(pha.z0, pha.z1).to_string())
print()
print("Intézkedéstípusok:", {TIPUS[int(k)]: int(v) for k, v in pha.tipus.value_counts().sort_index().items()})
print()
print(pha.groupby("energia").agg(veszely=("id", "count"), max_S0=("S0", "max"), max_S1=("S1", "max")).to_string())
'''),
    md("## Ábra"),
    code('''
SZIN = {"elfogadhatatlan": "#B83A3A", "ALARP": "#E07B39", "elfogadható": "#3E8E63"}
JEL = {1: "o", 2: "s", 3: "^"}
d = pha.assign(i0=pha.S0 + pha.P0, i1=pha.S1 + pha.P1).sort_values("i0")
fig, ax = plt.subplots(figsize=(10, 0.5 * len(d) + 1.4))
ax.axvspan(1.5, NARANCS - 0.5, color="#DDEFE4", zorder=0); ax.axvspan(NARANCS - 0.5, PIROS - 0.5, color="#FBE7D9", zorder=0)
ax.axvspan(PIROS - 0.5, 10.5, color="#F6DEDE", zorder=0)
for k, (_, r) in enumerate(d.iterrows()):
    ax.annotate("", xy=(r.i1, k), xytext=(r.i0, k), arrowprops=dict(arrowstyle="->", color="#285780", lw=1.6))
    ax.plot(r.i0, k, "o", color=SZIN[r.z0], ms=7)
    ax.plot(r.i1, k, JEL[int(r.tipus)], color=SZIN[r.z1], ms=8, mec="black", mew=0.5)
    if r.jelzes:
        ax.text(10.4, k, r.jelzes, fontsize=7, ha="right", va="center", color="#B83A3A")
ax.set_yticks(range(len(d))); ax.set_yticklabels([f"{a} {b}" for a, b in zip(d.id, d.veszely)], fontsize=8)
ax.set_xlim(1.5, 10.5); ax.set_xticks(range(2, 11)); ax.set_xlabel("S + P (a zónák alapja)")
for t, m in JEL.items():
    ax.plot([], [], m, color="#666666", label=f"{t}: {TIPUS[t]}")
ax.legend(fontsize=8, loc="lower right", title="maradó kockázat, intézkedéstípus", title_fontsize=8)
ax.set_title("Kockázatcsökkentés veszélyenként (kör: kiinduló, jelölő: maradó)", fontsize=10)
plt.tight_layout(); plt.savefig("pha_csokkentes.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A KoboCella nyolc veszélyéből egy (az ergonómiai terhelés) indult az elfogadhatatlan zónából; a kezelés után egy veszély (az áramütés) maradt a tűrhető tartományban, írásos ALARP-indoklással.
- Az intézkedések többsége tervezési vagy műszaki védőintézkedés; tájékoztatásra (egyéni védőeszközre) csak egy kis súlyosságú veszélynél (H7) támaszkodik a csapat. Súlyos veszélynél a csak tájékoztató intézkedést a notebook megjelöli.
- Az energiaforrások szerinti összesítés megmutatja, mely energiafajták felé kell a részletesebb elemzésnek (FMEA, hibafa, STPA) fordulnia.
"""),
]
