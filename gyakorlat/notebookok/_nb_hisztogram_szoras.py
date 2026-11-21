import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "sablonok"))
from _hisztogram_adat import ADAT, TURES  # noqa: E402
from _kozos import BETOLTO, code, fejresz, md  # noqa: E402

NEV = "hisztogram_szoras"
CIM = "Hisztogram, rétegzés és szórásdiagram: eloszlás, képesség rétegenként, korreláció és regresszió"

_ADAT = "[\n" + "".join(f"    ({t!r}, {x}, {y}),\n" for _, t, x, y in ADAT) + "]"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. hisztogramon mutatja egy mért jellemző eloszlását a tűrésmezőben, normális eloszlást illeszt, és normalitásvizsgálatot végez;
2. rétegzi az adatokat, rétegenként számol leíró statisztikákat és képességindexeket (Pp, Ppk), és megvizsgálja, különböznek-e a rétegek;
3. szórásdiagramon vizsgálja két változó kapcsolatát (korreláció, regresszió, konfidenciaintervallum) összesen és rétegenként.

A beépített példa a KoboCella két beérkező csavartételének csavarozási próbája (kézikönyv 25. fejezet; Ishikawa, 1982; Montgomery, 2020; NASA RP-1358, 5.1, 5.5, 5.7).
""", sablon="hisztogram_szoras_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Hisztogram, szórás- és rétegzett diagram eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött hisztogram_szoras_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("hisztogram_szoras_sablon.xlsx")
    d = pd.read_excel(fajl, sheet_name="Adatok", header=3).iloc[:300, 1:4]
    d.columns = ["reteg", "x", "y"]
    d = d[pd.to_numeric(d.y, errors="coerce").notna()].reset_index(drop=True)
    t = pd.read_excel(fajl, sheet_name="Statisztika", header=None, nrows=3)
    ATH, FTH = float(t.iloc[2, 1]), float(t.iloc[2, 3])
else:
    d = pd.DataFrame(''' + _ADAT + ''', columns=["reteg", "x", "y"])
    ATH, FTH = ''' + repr(TURES) + '''
d[["x", "y"]] = d[["x", "y"]].apply(pd.to_numeric, errors="coerce")
d["reteg"] = d.reteg.fillna("(nincs réteg)")
print(f"{len(d)} mérés, rétegek: {', '.join(d.reteg.unique())}; tűrés {ATH}–{FTH}")
'''),
    md("""## Eloszlás és képesség

A Pp és Ppk a teljes szórással számol; rétegzett adatnál a rétegek különbsége a teljes szórást megnöveli, ezért az összesített index rosszabb lehet, mint bármelyik rétegé (Montgomery, 2020)."""),
    code('''
def leiro(y):
    m, s = y.mean(), y.std(ddof=1)
    return pd.Series({"n": len(y), "átlag": m, "szórás": s, "medián": y.median(), "min": y.min(), "max": y.max(),
                      "Pp": (FTH - ATH) / (6 * s), "Ppk": min(FTH - m, m - ATH) / (3 * s),
                      "Shapiro–Wilk p": stats.shapiro(y).pvalue if len(y) >= 3 else np.nan})
T = pd.concat({"összesen": leiro(d.y), **{r: leiro(g.y) for r, g in d.groupby("reteg")}}, axis=1)
print(T.round(4).to_string())
gr = [g.y.to_numpy() for _, g in d.groupby("reteg")]
if len(gr) == 2:
    t_ = stats.ttest_ind(*gr, equal_var=False)
    print(f"\\nA két réteg átlagának különbsége: {gr[0].mean() - gr[1].mean():.4f}; Welch-féle t-próba p = {t_.pvalue:.2e}")
elif len(gr) > 2:
    print(f"\\nEgyutas varianciaelemzés p = {stats.f_oneway(*gr).pvalue:.2e}")
'''),
    md("## Szórásdiagram, korreláció és regresszió"),
    code('''
def regresszio(x, y):
    r = stats.linregress(x, y)
    return pd.Series({"n": len(x), "r": r.rvalue, "meredekség": r.slope, "tengelymetszet": r.intercept, "p": r.pvalue,
                      "meredekség 95% alsó": r.slope - stats.t.ppf(0.975, len(x) - 2) * r.stderr,
                      "meredekség 95% felső": r.slope + stats.t.ppf(0.975, len(x) - 2) * r.stderr})
dd = d.dropna(subset=["x", "y"])
Rg = pd.concat({"összesen": regresszio(dd.x, dd.y), **{r: regresszio(g.x, g.y) for r, g in dd.groupby("reteg")}}, axis=1)
print(Rg.round(5).to_string())
'''),
    md("## Ábra"),
    code('''
SZ = ["#285780", "#E07B39", "#3E8E63", "#7A5C99"]
fig, ax = plt.subplots(1, 3, figsize=(17, 4.8))
bins = np.arange(min(ATH, d.y.min()) - 0.01, max(FTH, d.y.max()) + 0.02, 0.02)
ax[0].hist(d.y, bins=bins, color="#A9C4DE", edgecolor="white")
xs = np.linspace(bins[0], bins[-1], 300)
ax[0].plot(xs, stats.norm.pdf(xs, d.y.mean(), d.y.std(ddof=1)) * len(d) * 0.02, color="#285780")
for t in (ATH, FTH): ax[0].axvline(t, color="#B83A3A", lw=1.2)
ax[0].set_title(f"Hisztogram (Ppk {T.loc['Ppk', 'összesen']:.2f})".replace(".", ",")); ax[0].set_xlabel("y")
ax[0].spines[["top", "right"]].set_visible(False)

for i, (r, g) in enumerate(d.groupby("reteg")):
    ax[1].hist(g.y, bins=bins, alpha=0.6, color=SZ[i % 4], edgecolor="white", label=f"{r} (Ppk {T.loc['Ppk', r]:.2f})".replace(".", ","))
for t in (ATH, FTH): ax[1].axvline(t, color="#B83A3A", lw=1.2)
ax[1].set_title("Rétegzett hisztogram"); ax[1].legend(frameon=False, fontsize=8); ax[1].set_xlabel("y")
ax[1].spines[["top", "right"]].set_visible(False)

for i, (r, g) in enumerate(dd.groupby("reteg")):
    ax[2].scatter(g.x, g.y, s=14, color=SZ[i % 4], alpha=0.75, label=r)
    lr = stats.linregress(g.x, g.y); xx = np.linspace(g.x.min(), g.x.max(), 50)
    ax[2].plot(xx, lr.intercept + lr.slope * xx, color=SZ[i % 4], lw=1.5)
ax[2].set_xlabel("x"); ax[2].set_ylabel("y"); ax[2].legend(frameon=False, fontsize=8)
ax[2].set_title(f"Szórásdiagram (összesen r = {Rg.loc['r', 'összesen']:.2f})".replace(".", ","))
ax[2].spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig("hisztogram_szoras.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""## Értelmezés

- Az összesített hisztogram széles; a rétegzés megmutatja, hogy két, egyenként keskeny eloszlás összegéről van szó: a B tétel átlaga kb. 0,07 Nm-rel kisebb. Az összesített Ppk (kb. 1,0) rosszabb, mint az A tételé (kb. 1,5), és közel a B tételéhez.
- A bitbetét használata és a nyomaték között gyenge, a kétlépcsős stratégiánál várt negatív kapcsolat látszik (kb. −0,002 Nm ezer csavarozásonként az A tételnél, határeset p-értékkel); a tételhatás ennél sokkal nagyobb.
- A korreláció nem bizonyít okságot: a tétel és a nyomaték kapcsolatát a beszállítóval közös vizsgálat (a bevonat elemzése) igazolta.
"""),
]
