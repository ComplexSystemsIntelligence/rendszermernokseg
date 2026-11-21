from _kozos import BETOLTO, code, fejresz, md

NEV = "hasznalhatosagi_teszt"
CIM = "Használhatósági teszt: feladatsiker, idő, SUS, problémafeltárás és mintaelemszám"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. kiértékeli a használhatósági teszt eredményeit: feladatonkénti sikerarány módosított Wald-intervallummal, az idők mértani átlaga, SUS-átlag konfidenciaintervallummal;
2. a probléma–résztvevő mátrixból megbecsüli az észlelés valószínűségét, és összeveti a megfigyelt és a modell szerinti problémafeltárást;
3. megtervezi a résztvevők számát formatív (problémafeltáró) és összegző (célérték-igazoló) tesztre;
4. beépített példával két prototípust is összevet.

A beépített példa a VárosiBringa kölcsönző alkalmazásának két prototípusa, 12 résztvevővel (kézikönyv 11. és 24. fejezet; ISO 9241-11; Nielsen és Landauer, 1993; Agresti és Coull, 1998; Sauro és Lewis, 2016).
""", sablon="hasznalhatosagi_teszt_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Használhatósági teszt eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött hasznalhatosagi_teszt_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
rng = np.random.default_rng(1)
'''),
    md("## Adatok"),
    code('''
FELADAT = ["F1 kölcsönzés", "F2 dokkoló keresése", "F3 vendégfizetés", "F4 visszaadás"]
CELIDO = [90, 60, 180, 60]
if SAJAT_SABLON:
    fajl = sablon_betoltese("hasznalhatosagi_teszt_sablon.xlsx")
    rv = pd.read_excel(fajl, sheet_name="Résztvevők", header=3).iloc[:30, :4]
    rv.columns = ["id", "csoport", "megj", "sus"]; rv = rv[rv.id.notna()].reset_index(drop=True)
    fe = pd.read_excel(fajl, sheet_name="Feladatok", header=3).iloc[:8, :4]
    fe.columns = ["id", "nev", "krit", "celido"]; fe = fe[fe.id.notna()].reset_index(drop=True)
    FELADAT = [f"{a} {b}" for a, b in zip(fe.id, fe.nev)]; CELIDO = list(pd.to_numeric(fe.celido))
    er = pd.read_excel(fajl, sheet_name="Eredmények", header=None, skiprows=5).iloc[:len(rv), 1:1 + 2 * len(fe)]
    siker = er.iloc[:, 0::2].apply(pd.to_numeric, errors="coerce").to_numpy()
    ido = er.iloc[:, 1::2].apply(pd.to_numeric, errors="coerce").to_numpy()
    pr = pd.read_excel(fajl, sheet_name="Problémák", header=3).iloc[:30, :4 + len(rv)]
    pr = pr[pr.iloc[:, 0].notna()].reset_index(drop=True)
    M = pr.iloc[:, 4:4 + len(rv)].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy().astype(int)
    sus = pd.to_numeric(rv.sus, errors="coerce").dropna().to_numpy()
    MASODIK = None
else:
    siker = np.array([[1, 1, 0, 1], [1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 0, 1], [1, 1, 1, 1], [1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 1, 1],
                      [1, 1, 0, 0], [1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]], dtype=float)
    ido = np.array([[74, 48, np.nan, 41], [52, 35, 150, 30], [96, np.nan, np.nan, 58], [81, 55, np.nan, 47], [48, 31, 131, 28],
                    [118, np.nan, np.nan, 66], [np.nan, 71, np.nan, 62], [57, 38, 162, 33], [102, 64, np.nan, np.nan], [69, 44, 174, 39],
                    [91, np.nan, np.nan, 52], [88, 60, 196, 49]])
    sus = np.array([62.5, 72.5, 52.5, 60.0, 80.0, 47.5, 45.0, 75.0, 57.5, 70.0, 55.0, 90.0])
    M = np.zeros((8, 12), dtype=int)
    for u, kik in enumerate([[1, 3, 4, 6, 7, 11], [3, 6, 11], [2, 5, 9, 12], [4, 7, 10], [1, 2, 4, 5, 8, 10, 12], [3, 11], [2, 6, 9], [10]]):
        M[u, [k - 1 for k in kik]] = 1
    # a második prototípus (javított változat) ugyanazokkal a résztvevőkkel
    MASODIK = dict(
        siker=np.array([[1, 1, 1, 1]] * 6 + [[1, 1, 0, 1]] + [[1, 1, 1, 1]] * 3 + [[1, 1, 1, 0]] + [[1, 1, 1, 1]], dtype=float),
        sus=np.array([77.5, 75.0, 75.0, 85.0, 77.5, 72.5, 67.5, 85.0, 82.5, 82.5, 72.5, 95.0]))
n_r, n_f = siker.shape
print(f"{n_r} résztvevő, {n_f} feladat, {M.shape[0]} probléma")
'''),
    md("""## Hatásosság és hatékonyság

A sikerarány intervalluma a módosított Wald-módszer (Agresti és Coull, 1998). A feladatidők eloszlása jobbra ferde, ezért kis mintán a mértani átlag a medián jobb becslése (Sauro és Lewis, 2016); az intervallumot a logaritmált időkön számoljuk."""),
    code('''
def modositott_wald(x, n, konf=0.95):
    z = stats.norm.ppf(1 - (1 - konf) / 2)
    pt = (x + z * z / 2) / (n + z * z); h = z * np.sqrt(pt * (1 - pt) / (n + z * z))
    return max(0.0, pt - h), min(1.0, pt + h)

def mertani(t, konf=0.95):
    t = t[~np.isnan(t)]
    if len(t) < 2:
        return (np.nan,) * 3
    l = np.log(t); m, s = l.mean(), l.std(ddof=1); tk = stats.t.ppf(1 - (1 - konf) / 2, len(t) - 1)
    return np.exp(m), np.exp(m - tk * s / np.sqrt(len(t))), np.exp(m + tk * s / np.sqrt(len(t)))

def feladat_tabla(siker, ido=None):
    sorok = []
    for k in range(siker.shape[1]):
        s = siker[:, k][~np.isnan(siker[:, k])]; x, n = int(s.sum()), len(s)
        a, f = modositott_wald(x, n)
        sor = {"feladat": FELADAT[k], "siker": f"{x}/{n}", "arány": x / n, "alsó": a, "felső": f}
        if ido is not None:
            g, ga, gf = mertani(ido[:, k]); sor.update({"idő (mértani)": g, "idő alsó": ga, "idő felső": gf, "célidő": CELIDO[k]})
        sorok.append(sor)
    return pd.DataFrame(sorok)

T1 = feladat_tabla(siker, ido)
print(T1.round(2).to_string(index=False))
x, n = int(np.nansum(siker)), int(np.sum(~np.isnan(siker)))
print(f"\\nÖsszes feladat: {x}/{n} = {x / n:.0%}; 95%-os intervallum {modositott_wald(x, n)[0]:.0%}–{modositott_wald(x, n)[1]:.0%}")
'''),
    md("## Elégedettség (SUS)"),
    code('''
def sus_int(s, konf=0.95):
    m, sd = s.mean(), s.std(ddof=1); tk = stats.t.ppf(1 - (1 - konf) / 2, len(s) - 1)
    return m, m - tk * sd / np.sqrt(len(s)), m + tk * sd / np.sqrt(len(s))

m, a, f = sus_int(sus)
print(f"SUS: {m:.1f} (95%: {a:.1f}–{f:.1f}); viszonyítás: 68")
if MASODIK is not None:
    m2, a2, f2 = sus_int(MASODIK["sus"])
    print(f"2. prototípus SUS: {m2:.1f} (95%: {a2:.1f}–{f2:.1f})")
    d = MASODIK["sus"] - sus
    print(f"Különbség ugyanazoknál a résztvevőknél: {d.mean():+.1f} pont, páros t-próba p = {stats.ttest_rel(MASODIK['sus'], sus).pvalue:.4f}")
'''),
    md("""## Problémafeltárás

Az észlelés átlagos valószínűsége $p$ = az észlelések száma / (problémák × résztvevők). A modell szerint $n$ résztvevő a problémák $1-(1-p)^n$ hányadát tárja fel (Nielsen és Landauer, 1993). A megfigyelt görbét a résztvevők véletlen sorrendjeinek átlagaként számoljuk. Kis mintán a $p$ becslése felfelé torzít, mert a fel nem tárt problémák nem szerepelnek a mátrixban (Sauro és Lewis, 2016)."""),
    code('''
p = M.sum() / M.size
egyszeri = int((M.sum(axis=1) == 1).sum())
print(f"p = {p:.3f}; {egyszeri} probléma csak egy résztvevőnél jelentkezett")
print(f"Modell: {n_r} résztvevő → {1 - (1 - p) ** n_r:.0%}; 5 résztvevő → {1 - (1 - p) ** 5:.0%}")
megfigyelt = np.zeros(n_r)
for _ in range(2000):
    sorrend = rng.permutation(n_r)
    megfigyelt += [(M[:, sorrend[:k + 1]].sum(axis=1) > 0).mean() for k in range(n_r)]
megfigyelt /= 2000
'''),
    md("""## A résztvevők számának tervezése

**Formatív teszt:** hány résztvevő tárja fel a problémák adott hányadát ($P$)? $n \\ge \\ln(1-P)/\\ln(1-p)$.

**Összegző teszt:** hány résztvevő kell ahhoz, hogy várható sikerarány mellett a módosított Wald-intervallum alsó határa elérje a célértéket?"""),
    code('''
for pp in (0.1, 0.2, 0.31, p):
    print(f"p = {pp:.2f}: a problémák 85%-ához {int(np.ceil(np.log(0.15) / np.log(1 - pp)))}, 95%-ához {int(np.ceil(np.log(0.05) / np.log(1 - pp)))} résztvevő")

def osszegzo_n(vart, cel, konf=0.95, nmax=3000):
    for n in range(5, nmax):
        if modositott_wald(round(vart * n), n, konf)[0] >= cel:
            return n
    return None

CEL = 0.85
vartak = np.round(np.arange(0.87, 0.981, 0.01), 2)
szuks = [osszegzo_n(v, CEL) for v in vartak]
for v, s in zip(vartak, szuks):
    print(f"várható arány {v:.0%}, cél ≥ {CEL:.0%}: {s} résztvevő")
'''),
    md("## Ábra"),
    code('''
fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
xs = np.arange(n_f)
def hibasav(axx, T, eltol, szin, cimke):
    axx.errorbar(xs + eltol, T["arány"], yerr=[T["arány"] - T["alsó"], T["felső"] - T["arány"]], fmt="o", color=szin, capsize=4, label=cimke)
hibasav(ax[0], T1, -0.12 if MASODIK is not None else 0, "#B83A3A" if MASODIK is not None else "#285780", "1. prototípus" if MASODIK is not None else "sikerarány")
if MASODIK is not None:
    hibasav(ax[0], feladat_tabla(MASODIK["siker"]), 0.12, "#285780", "2. prototípus")
ax[0].set_xticks(xs); ax[0].set_xticklabels([f.split(" ")[0] for f in FELADAT]); ax[0].set_ylim(0, 1.05)
ax[0].set_ylabel("sikerarány (95%-os intervallum)"); ax[0].set_title("Feladatsiker"); ax[0].legend(fontsize=8, frameon=False, loc="lower left")
ax[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}")); ax[0].grid(alpha=0.3); ax[0].spines[["top", "right"]].set_visible(False)

nn = np.arange(1, n_r + 1)
ax[1].plot(nn, 100 * megfigyelt, "o", color="#285780", label="megfigyelt (véletlen sorrendek átlaga)")
ax[1].plot(np.linspace(0, n_r, 100), 100 * (1 - (1 - p) ** np.linspace(0, n_r, 100)), color="#E07B39", label=f"modell, p = {p:.2f}".replace(".", ","))
ax[1].set_xlabel("résztvevők száma"); ax[1].set_ylabel("a feltárt problémák aránya [%]"); ax[1].set_ylim(0, 105)
ax[1].set_title("Problémafeltárás"); ax[1].legend(fontsize=8, frameon=False, loc="lower right"); ax[1].grid(alpha=0.3); ax[1].spines[["top", "right"]].set_visible(False)

ax[2].plot(100 * vartak, szuks, "o-", color="#285780")
ax[2].set_yscale("log"); ax[2].set_xlabel("várható sikerarány [%]"); ax[2].set_ylabel("szükséges résztvevők")
ax[2].set_title(f"Összegző teszt: alsó határ ≥ {CEL:.0%}"); ax[2].grid(alpha=0.3, which="both"); ax[2].spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig("hasznalhatosagi_teszt.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""## Értelmezés

- A 12 fős formatív teszt a problémák becslés szerint mintegy 98%-át feltárta; a csak egyszer észlelt probléma jelzi, hogy a valóságban ennél valamivel kevesebbet.
- A sikerarányok intervallumai 12 résztvevőnél szélesek: a teszt alkalmas a problémák feltárására és két változat durva összevetésére, de nem alkalmas egy 85–90%-os célérték igazolására.
- Az összegző teszt résztvevőszáma gyorsan nő, ahogy a várható arány közelít a célértékhez; ilyenkor az üzemi adatok (naplók) adnak elég nagy mintát.
"""),
]
