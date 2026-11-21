from _kozos import BETOLTO, code, fejresz, md

NEV = "tlx_sus"
CIM = "NASA-TLX és SUS: munkaterhelés és használhatóság kiértékelése, két változat páros összevetése"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. kiszámítja a nyers és a súlyozott NASA-TLX-értékeket, és két feltételt páros t-próbával és Wilcoxon-próbával vet össze;
2. kiszámítja a SUS-pontszámokat, a konfidenciaintervallumot, és Bangor és munkatársai melléknévi skáláján értelmezi az átlagot;
3. a feladatsikert korrigált Wald-intervallummal becsli (Sauro és Lewis ajánlása kis mintákra);
4. ábrán mutatja az alskálánkénti és a résztvevőnkénti változást.

A beépített példák: NASA-TLX – a KoboCella nyolc kezelője a kézi szerelésben és a kísérleti cellában; SUS – a VárosiBringa alkalmazás két prototípusa tizenkét résztvevővel (kézikönyv 11. fejezet).
""", sablon="tlx_sus_sablon.xlsx", eszkozlap="Gyakorlati útmutató, NASA-TLX és SUS eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött tlx_sus_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
ALSKALAK = ["szellemi", "fizikai", "időbeli", "teljesítmény", "erőfeszítés", "frusztráció"]
'''),
    md("## Adatok"),
    code('''
def blokkok(nyers, ncol):
    """A 'Résztvevő' fejlécű blokkok kitöltött sorai (az első oszlop kitöltött, a számadatok teljesek)."""
    fej = list(nyers.index[nyers.iloc[:, 0] == "Résztvevő"])
    ki = []
    for f in fej:
        b = []
        for r in range(f + 1, len(nyers)):
            v = nyers.iloc[r, 0]
            if not isinstance(v, str) or v in ("Átlag", "Résztvevők száma", "Összesen"):
                break
            sor = pd.to_numeric(nyers.iloc[r, 1:1 + ncol], errors="coerce")
            if sor.notna().all():
                b.append(sor.to_numpy(float))
        ki.append(np.array(b))
    return ki

if SAJAT_SABLON:
    fajl = sablon_betoltese("tlx_sus_sablon.xlsx")
    W = blokkok(pd.read_excel(fajl, sheet_name="Súlyok", header=None), 6)[0]
    A, B = blokkok(pd.read_excel(fajl, sheet_name="NASA-TLX", header=None), 6)[:2]
    S1, S2 = blokkok(pd.read_excel(fajl, sheet_name="SUS", header=None), 10)[:2]
    fs = pd.read_excel(fajl, sheet_name="Feladatsiker", header=None)
    F1 = fs.iloc[5:25, 1:5].apply(pd.to_numeric, errors="coerce").dropna(how="all").to_numpy(float)
    F2 = fs.iloc[5:25, 8:12].apply(pd.to_numeric, errors="coerce").dropna(how="all").to_numpy(float)
else:
    A = np.array([[30, 60, 65, 50, 50, 20], [35, 55, 50, 40, 80, 30], [45, 55, 50, 25, 65, 35], [40, 50, 60, 20, 40, 25],
                  [20, 50, 40, 35, 70, 25], [40, 65, 65, 25, 60, 50], [50, 40, 45, 45, 50, 35], [35, 65, 65, 35, 85, 35]], float)
    B = np.array([[40, 30, 30, 25, 40, 30], [45, 15, 30, 5, 50, 20], [60, 40, 45, 20, 50, 10], [30, 10, 35, 15, 30, 30],
                  [45, 35, 25, 15, 45, 20], [25, 25, 50, 15, 60, 35], [30, 25, 55, 30, 35, 20], [40, 15, 30, 15, 55, 25]], float)
    W = np.array([[3, 4, 3, 2, 3, 0], [3, 4, 4, 1, 3, 0], [3, 3, 4, 2, 2, 1], [2, 5, 4, 1, 3, 0], [2, 3, 5, 0, 4, 1],
                  [4, 4, 4, 0, 2, 1], [1, 4, 4, 2, 4, 0], [4, 3, 5, 1, 2, 0]], float)
    S1 = np.array([[4, 4, 5, 2, 3, 2, 3, 3, 4, 3], [5, 2, 4, 2, 4, 2, 3, 2, 4, 3], [3, 3, 4, 2, 3, 2, 1, 4, 4, 3], [4, 4, 3, 5, 5, 3, 4, 2, 4, 2],
                  [5, 1, 5, 2, 3, 2, 3, 1, 4, 2], [3, 3, 3, 3, 3, 4, 3, 3, 3, 3], [3, 5, 3, 3, 4, 3, 3, 3, 2, 3], [4, 2, 4, 1, 4, 2, 2, 2, 4, 1],
                  [2, 2, 3, 3, 3, 3, 2, 1, 3, 1], [4, 2, 3, 2, 4, 2, 4, 3, 4, 2], [3, 3, 3, 3, 3, 3, 3, 2, 4, 3], [5, 2, 5, 2, 5, 2, 4, 1, 5, 1]], float)
    S2 = np.array([[4, 2, 3, 1, 4, 2, 4, 1, 4, 2], [4, 2, 4, 2, 3, 2, 5, 3, 4, 1], [4, 2, 4, 2, 4, 2, 4, 2, 3, 1], [5, 1, 4, 3, 4, 2, 4, 1, 5, 1],
                  [4, 2, 5, 1, 3, 2, 4, 1, 3, 2], [4, 2, 4, 4, 3, 2, 4, 1, 5, 2], [2, 2, 4, 3, 5, 1, 4, 3, 4, 3], [5, 1, 5, 3, 5, 2, 5, 2, 4, 2],
                  [3, 1, 3, 1, 4, 1, 5, 3, 5, 1], [4, 2, 4, 1, 3, 2, 5, 1, 4, 1], [4, 3, 4, 2, 4, 3, 4, 1, 4, 2], [5, 1, 4, 1, 5, 1, 5, 1, 5, 2]], float)
    F1 = np.array([[1, 1, 0, 1], [1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 0, 1], [1, 1, 1, 1], [1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 1, 1],
                   [1, 1, 0, 0], [1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]], float)
    F2 = np.array([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 0, 1], [1, 1, 1, 1],
                   [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 0], [1, 1, 1, 1]], float)
assert (W.sum(axis=1) == 15).all(), "A TLX-súlyok soronkénti összege 15 kell legyen"
print(f"TLX: {len(A)} résztvevő; SUS: {len(S1)} résztvevő; feladatsiker: {F1.shape[1]} feladat")
'''),
    md("## NASA-TLX"),
    code('''
def paros(x, y, nev):
    """Azonos résztvevők két mérése. Eltérő résztvevőknél kétmintás próba kell:
    stats.ttest_ind(y, x, equal_var=False) és stats.mannwhitneyu(y, x)."""
    d = y - x
    t = stats.ttest_rel(y, x)
    w = stats.wilcoxon(y, x)
    dz = d.mean() / d.std(ddof=1)
    ci = stats.t.interval(0.95, len(d) - 1, loc=d.mean(), scale=stats.sem(d))
    print(f"{nev}: {x.mean():.1f} -> {y.mean():.1f}, különbség {d.mean():+.1f} (95% CI {ci[0]:+.1f} … {ci[1]:+.1f}); "
          f"páros t = {t.statistic:.2f}, p = {t.pvalue:.2g}; Wilcoxon p = {w.pvalue:.2g}; hatásméret dz = {dz:.2f}")

nyersA, nyersB = A.mean(axis=1), B.mean(axis=1)
sulyA, sulyB = (A * W).sum(axis=1) / 15, (B * W).sum(axis=1) / 15
paros(nyersA, nyersB, "Nyers TLX")
paros(sulyA, sulyB, "Súlyozott TLX")
print("\\nAlskálánkénti átlagok (A -> B):")
for j, a in enumerate(ALSKALAK):
    print(f"  {a:13s} {A[:, j].mean():5.1f} -> {B[:, j].mean():5.1f}   ({B[:, j].mean() - A[:, j].mean():+.1f})")
print("\\nÁtlagos súly (a terhelés forrásai):", {a: round(float(v), 2) for a, v in zip(ALSKALAK, W.mean(axis=0) / 15)})
'''),
    md("## SUS és feladatsiker"),
    code('''
def sus(X):
    paratlan = X[:, 0::2] - 1
    paros_ = 5 - X[:, 1::2]
    return 2.5 * (paratlan.sum(axis=1) + paros_.sum(axis=1))

BANGOR = [(12.5, "legrosszabb elképzelhető"), (20.3, "szörnyű"), (35.7, "gyenge"), (50.9, "megfelelő (OK)"),
          (71.4, "jó"), (85.5, "kiváló"), (90.9, "legjobb elképzelhető")]
def melleknev(x):
    """A két szomszédos melléknév, amelyek átlagpontszáma közé x esik (Bangor és mtsai, 2009)."""
    for (a, na), (b, nb) in zip(BANGOR, BANGOR[1:]):
        if a <= x <= b:
            return f"a „{na}” ({a}) és a „{nb}” ({b}) között, a „{na if x - a < b - x else nb}” minősítéshez közelebb"
    return f"„{BANGOR[0][1]}” alatt" if x < BANGOR[0][0] else f"„{BANGOR[-1][1]}” felett"

def elfogadhatosag(x):
    return "elfogadható" if x >= 70 else ("elfogadhatatlan" if x < 50 else "határeset")

s1, s2 = sus(S1), sus(S2)
for nev, s in (("1. prototípus", s1), ("2. prototípus", s2)):
    ci = stats.t.interval(0.95, len(s) - 1, loc=s.mean(), scale=stats.sem(s))
    print(f"{nev}: SUS = {s.mean():.1f} (95% CI {ci[0]:.1f} … {ci[1]:.1f}); "
          f"melléknévi skálán {melleknev(s.mean())}; {elfogadhatosag(s.mean())}; átlag (68) felett: {s.mean() > 68}")
paros(s1, s2, "SUS")

def adj_wald(x, n, z=1.96):
    p = (x + z**2 / 2) / (n + z**2)
    h = z * np.sqrt(p * (1 - p) / (n + z**2))
    return max(0, p - h), min(1, p + h)

print()
for nev, F in (("1. prototípus", F1), ("2. prototípus", F2)):
    x, n = F.sum(), F.size
    lo, hi = adj_wald(x, n)
    print(f"{nev}: feladatsiker {x:.0f}/{n} = {x / n:.0%} (korrigált Wald 95% CI {lo:.0%} … {hi:.0%}); "
          f"feladatonként: {(F.mean(axis=0) * 100).round(0).tolist()} %")
'''),
    md("## Ábra"),
    code('''
fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
x = np.arange(6); sz = 0.38
axs[0].bar(x - sz / 2, A.mean(axis=0), sz, color="#B8CEE4", label="A: kézi szerelés")
axs[0].bar(x + sz / 2, B.mean(axis=0), sz, color="#285780", label="B: kísérleti cella")
axs[0].errorbar(x - sz / 2, A.mean(axis=0), yerr=stats.sem(A, axis=0), fmt="none", ecolor="#555555", capsize=3)
axs[0].errorbar(x + sz / 2, B.mean(axis=0), yerr=stats.sem(B, axis=0), fmt="none", ecolor="#555555", capsize=3)
axs[0].set_xticks(x); axs[0].set_xticklabels(ALSKALAK, fontsize=8); axs[0].set_ylim(0, 100); axs[0].set_ylabel("0–100")
axs[0].set_title(f"NASA-TLX alskálák (átlag ± SE); nyers TLX {nyersA.mean():.1f} -> {nyersB.mean():.1f}", fontsize=10)
axs[0].legend(fontsize=8); axs[0].grid(axis="y", alpha=0.3)
for a, b in zip(s1, s2):
    axs[1].plot([0, 1], [a, b], color="#7FA6CC", alpha=0.8, marker="o", ms=4)
axs[1].plot([0, 1], [s1.mean(), s2.mean()], color="#285780", lw=3, marker="s", ms=8, label="átlag")
for v, t, va in ((50, "elfogadhatatlan alatta", "center"), (68, "átlag (68)", "top"), (70, "elfogadható felette", "bottom")):
    axs[1].axhline(v, color="#999999", ls=":" if v != 68 else "--", lw=1)
    axs[1].text(1.04, v + (0.4 if va == "bottom" else -0.4 if va == "top" else 0), t, fontsize=7.5, va=va)
axs[1].set_xticks([0, 1]); axs[1].set_xticklabels(["1. prototípus", "2. prototípus"]); axs[1].set_xlim(-0.2, 1.55)
axs[1].set_ylim(30, 100); axs[1].set_ylabel("SUS-pontszám"); axs[1].legend(fontsize=8, loc="lower right")
axs[1].set_title(f"SUS résztvevőnként: {s1.mean():.1f} -> {s2.mean():.1f}", fontsize=10); axs[1].grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig("tlx_sus.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- **NASA-TLX.** A kísérleti cellában a nyers TLX 45,9-ről 31,4-re, a súlyozott 50,8-ról 33,8-ra csökkent; mind a nyolc kezelőnél csökkent, a különbség a páros t-próba és a Wilcoxon-próba szerint is szignifikáns. A csökkenés döntően a fizikai igénybevételből (−30,6 pont), az időbeli nyomásból és az erőfeszítésből jön; a szellemi igénybevétel kissé nőtt (+2,5), mert a kezelőnek a HMI visszajelzéseit is figyelnie kell. A terhelés tehát átrendeződött, nem tűnt el.
- **SUS.** Az 1. prototípus átlaga 64,0 (határeset, az átlagos 68 alatt, széles intervallummal), a 2. prototípusé 79,0 (elfogadható, a „jó” és a „kiváló” melléknév között). Két résztvevő pontszáma alig változott, a többieké 10–25 ponttal nőtt. A feladatsiker 75%-ról 96%-ra nőtt; a legnagyobb javulás a vendégfizetésnél (F3: 42% → 92%) volt, ahol az első prototípusnál a résztvevők több mint fele elakadt.
- **Óvatosság.** Nyolc, illetve tizenkét résztvevő kis minta: a konfidenciaintervallumok szélesek, ezért a döntést a megfigyelt hibák és a résztvevők megjegyzései is alátámasztják, nem csak a pontszámok. A SUS-pontszám nem százalék, és a feladatsikerrel együtt értelmezendő.
"""),
]
