import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "sablonok"))
from _wbs_adat import AC, CEL_HET, EV, PV, TEV, WBS  # noqa: E402
from _kozos import BETOLTO, code, fejresz, md  # noqa: E402

NEV = "wbs"
CIM = "Munkalebontás, hálós ütemterv, ütemezési kockázat (Monte Carlo) és megszerzett érték"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. ellenőrzi a munkalebontási struktúrát (100%-szabály), és összesíti a költségeket és a megszerzett értéket;
2. kritikus út módszerével ütemez (legkorábbi és legkésőbbi kezdés, tartalék, kritikus út);
3. a hárompontos becslésekből a klasszikus PERT-tel és Monte Carlo-szimulációval becsli a határidő teljesülésének valószínűségét, és kiszámolja a tevékenységek kritikussági indexét;
4. a megszerzett érték módszerével értékeli a projekt állapotát, és előrejelzi a befejezéskori költséget.

A beépített példa a KoboCella-projekt (kézikönyv 26. fejezet; MIL-STD-881F, 2022; Kelley és Walker, 1959; Malcolm és mtsai, 1959; Fleming és Koppelman, 2010; NASA SE Handbook, 6.1. szakasz).
""", sablon="wbs_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Munkalebontási struktúra (WBS) eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött wbs_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
rng = np.random.default_rng(26)
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("wbs_sablon.xlsx")
    w = pd.read_excel(fajl, sheet_name="WBS", header=3).iloc[:60, :5]
    w.columns = ["kod", "nev", "felelos", "koltseg", "kesz"]
    w = w[w.kod.notna()].copy(); w["kod"] = w.kod.astype(str)
    t = pd.read_excel(fajl, sheet_name="Ütemezés", header=5).iloc[:40, :12]
    t.columns = ["id", "nev", "wbs", "o", "m", "p", "te", "sd", "e1", "e2", "e3", "e4"]
    t = t[t.id.notna()].copy()
    t["elozok"] = [[str(x) for x in r if pd.notna(x) and str(x).strip()] for r in t[["e1", "e2", "e3", "e4"]].to_numpy()]
    CEL = float(pd.read_excel(fajl, sheet_name="Ütemezés", header=None, nrows=3).iloc[2, 2])
    e = pd.read_excel(fajl, sheet_name="Megszerzett érték", header=4).iloc[:24, :4]
    e.columns = ["honap", "pv", "ev", "ac"]; e = e[e.honap.notna()]
else:
    w = pd.DataFrame(''' + repr(WBS) + ''', columns=["kod", "nev", "felelos", "koltseg", "kesz"])
    t = pd.DataFrame(''' + repr(TEV) + ''', columns=["id", "nev", "wbs", "o", "m", "p", "elozok"])
    CEL = ''' + str(CEL_HET) + '''
    e = pd.DataFrame({"honap": range(1, 9), "pv": ''' + repr(PV) + ''',
                      "ev": ''' + repr(EV) + ''' + [np.nan] * 4, "ac": ''' + repr(AC) + ''' + [np.nan] * 4})
t[["o", "m", "p"]] = t[["o", "m", "p"]].astype(float)
print(f"WBS: {len(w)} elem; ütemezés: {len(t)} tevékenység; jóváhagyott időtartam {CEL:g} hét")
'''),
    md("## A munkalebontási struktúra és a 100%-szabály"),
    code('''
w["szint"] = w.kod.str.count(r"\\.") + 1
w["level"] = [not any(k2.startswith(k + ".") for k2 in w.kod) for k in w.kod]
w[["koltseg", "kesz"]] = w[["koltseg", "kesz"]].apply(pd.to_numeric, errors="coerce")
def osszeg(k, oszlop):
    m = w.kod.str.startswith(k + ".") & w.level
    return (w.loc[m, "koltseg"] * (w.loc[m, "kesz"] if oszlop == "ev" else 1)).sum()
w["osszkoltseg"] = [r.koltseg if r.level else osszeg(r.kod, "k") for r in w.itertuples()]
w["ev"] = [r.koltseg * r.kesz if r.level else osszeg(r.kod, "ev") for r in w.itertuples()]
BAC = w.loc[w.level, "koltseg"].sum()
hiba = w[(w.level & w.koltseg.isna()) | (~w.level & w.koltseg.notna())]
print(w.loc[w.szint == 1, ["kod", "nev", "osszkoltseg", "ev"]].round(2).to_string(index=False))
print(f"BAC = {BAC:.1f} MFt; a legfelső szintek összege {w.loc[w.szint == 1, 'osszkoltseg'].sum():.1f} MFt; "
      f"megszerzett érték {w.loc[w.level, 'ev'].sum():.1f} MFt")
print("A 100%-szabály teljesül." if hiba.empty else f"FIGYELEM: {len(hiba)} sor sérti a szabályt: {list(hiba.kod)}")
'''),
    md("## Kritikus út (legvalószínűbb időkkel)"),
    code('''
ids = list(t.id)
elozo = dict(zip(t.id, t.elozok))
def cpm(d):
    ES, EF = {}, {}
    for i in ids:
        ES[i] = max([EF[p] for p in elozo[i]], default=0.0); EF[i] = ES[i] + d[i]
    T = max(EF.values()); LF, LS = {}, {}
    for i in reversed(ids):
        ut = [k for k in ids if i in elozo[k]]
        LF[i] = min([LS[k] for k in ut], default=T); LS[i] = LF[i] - d[i]
    return ES, EF, LS, LF, T
ES, EF, LS, LF, T = cpm(dict(zip(t.id, t.m)))
t["ES"], t["EF"], t["tartalek"] = t.id.map(ES), t.id.map(EF), [LS[i] - ES[i] for i in t.id]
t["kritikus"] = t.tartalek.abs() < 1e-9
print(t[["id", "nev", "m", "ES", "EF", "tartalek", "kritikus"]].to_string(index=False))
print(f"\\nIdőtartam: {T:g} hét; kritikus út: {' → '.join(t.loc[t.kritikus, 'id'])}")
'''),
    md("""## Ütemezési kockázat: PERT és Monte Carlo

A klasszikus PERT a tevékenységidőket béta-eloszlással közelíti ($t_e = (o + 4m + p)/6$, $\\sigma = (p - o)/6$), és csak a kritikus úttal számol (Malcolm és mtsai, 1959). A Monte Carlo-szimuláció minden futásban újrasorsolja az időket (itt PERT-béta eloszlással) és újraszámolja a kritikus utat, így a párhuzamos, közel kritikus utak hatását is figyelembe veszi. A **kritikussági index** azt mutatja, a futások hány százalékában volt egy tevékenység a kritikus úton."""),
    code('''
t["te"] = (t.o + 4 * t.m + t.p) / 6; t["sd"] = (t.p - t.o) / 6
Te, sdT = t.loc[t.kritikus, "te"].sum(), np.sqrt((t.loc[t.kritikus, "sd"] ** 2).sum())
print(f"PERT: várható idő {Te:.1f} hét, szórás {sdT:.2f} hét, P(T ≤ {CEL:g}) = {stats.norm.cdf((CEL - Te) / sdT):.1%}")

def pert_beta(o, m, p, n):
    if p - o < 1e-9: return np.full(n, m)
    a = 1 + 4 * (m - o) / (p - o); b = 1 + 4 * (p - m) / (p - o)
    return o + (p - o) * rng.beta(a, b, n)
N = 20000
minta = {r.id: pert_beta(r.o, r.m, r.p, N) for r in t.itertuples()}
Tk, krit = np.empty(N), {i: 0 for i in ids}
for k in range(N):
    ES_, EF_, LS_, LF_, T_ = cpm({i: minta[i][k] for i in ids})
    Tk[k] = T_
    for i in ids:
        if abs(LS_[i] - ES_[i]) < 1e-9: krit[i] += 1
t["kritikussag"] = [krit[i] / N for i in t.id]
print(f"Monte Carlo: átlag {Tk.mean():.1f} hét, P80 {np.percentile(Tk, 80):.1f}, P(T ≤ {CEL:g}) = {(Tk <= CEL).mean():.1%}")
print(t.loc[t.kritikussag > 0.01, ["id", "nev", "kritikussag"]].sort_values("kritikussag", ascending=False).round(2).to_string(index=False))
'''),
    md("## Megszerzett érték"),
    code('''
e[["pv", "ev", "ac"]] = e[["pv", "ev", "ac"]].apply(pd.to_numeric, errors="coerce")
u = e.dropna(subset=["ev", "ac"]).iloc[-1]
SPI, CPI = u.ev / u.pv, u.ev / u.ac
EAC = BAC / CPI
print(f"{int(u.honap)}. hónap: PV {u.pv:g}, EV {u.ev:g}, AC {u.ac:g} MFt")
print(f"SV {u.ev - u.pv:+.1f}, CV {u.ev - u.ac:+.1f} MFt; SPI {SPI:.2f}, CPI {CPI:.2f}; EAC = {EAC:.1f} MFt (VAC {BAC - EAC:+.1f} MFt)")
print(f"Ha a hátralévő munka a tervezett költséghatékonysággal halad: EAC = AC + (BAC − EV) = {u.ac + BAC - u.ev:.1f} MFt")
'''),
    md("## Ábra"),
    code('''
fig, ax = plt.subplots(1, 3, figsize=(17, 5.2), gridspec_kw={"width_ratios": [1.4, 1, 1]})
for k, r in enumerate(t.itertuples()):
    if r.m == 0:
        ax[0].plot(r.ES, k, "D", color="#1B3A57", ms=6)
    else:
        ax[0].barh(k, r.m, left=r.ES, color="#285780" if r.kritikus else "#A9C4DE", height=0.6)
ax[0].set_yticks(range(len(t))); ax[0].set_yticklabels([f"{r.id} {r.nev}" for r in t.itertuples()], fontsize=7)
ax[0].invert_yaxis(); ax[0].axvline(CEL, color="#B83A3A", ls="--", lw=1); ax[0].set_xlabel("hét")
ax[0].set_title(f"Ütemterv: {T:g} hét (sötét: kritikus út)".replace(".", ","), fontsize=10)
ax[0].spines[["top", "right"]].set_visible(False)

ax[1].hist(Tk, bins=50, color="#A9C4DE", edgecolor="white")
ax[1].axvline(CEL, color="#B83A3A", lw=1.5); ax[1].axvline(T, color="#285780", ls="--", lw=1)
ax[1].text(CEL + 0.2, ax[1].get_ylim()[1] * 0.9, f"P(T ≤ {CEL:g}) = {(Tk <= CEL).mean():.0%}", color="#B83A3A", fontsize=9)
ax[1].set_xlabel("a projekt időtartama [hét]"); ax[1].set_yticks([]); ax[1].set_title("Monte Carlo-szimuláció", fontsize=10)
ax[1].spines[["top", "right", "left"]].set_visible(False)

ax[2].plot(e.honap, e.pv, "--", color="#6B7280", label="PV")
ax[2].plot(e.honap, e.ev, "o-", color="#285780", label="EV")
ax[2].plot(e.honap, e.ac, "s-", color="#B83A3A", label="AC")
ax[2].plot([u.honap, e.honap.max()], [u.ac, EAC], ":", color="#B83A3A", label=f"EAC {EAC:.1f}".replace(".", ","))
ax[2].axhline(BAC, color="#6B7280", lw=0.8); ax[2].set_xlabel("hónap"); ax[2].set_ylabel("MFt")
ax[2].legend(frameon=False, fontsize=8); ax[2].set_title(f"Megszerzett érték: SPI {SPI:.2f}, CPI {CPI:.2f}".replace(".", ","), fontsize=10)
ax[2].spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig("wbs.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""## Értelmezés

- A determinisztikus ütemterv 31 hét, négy hét tartalékkal a jóváhagyott 35 héthez képest; a kritikus utat a kobot beszerzése határozza meg.
- A klasszikus PERT csak a kritikus úttal számol; a Monte Carlo-szimuláció a közel kritikus utak (főként a csavarozó egység beszerzésének) hatását is mutatja, ezért a határidő teljesülésének valószínűsége kisebb.
- A negyedik hónap végén a projekt késésben van, és drágábban halad (SPI 0,88, CPI 0,90); ha a költséghatékonyság nem javul, a befejezéskori költség kb. 86,7 MFt.
"""),
]
