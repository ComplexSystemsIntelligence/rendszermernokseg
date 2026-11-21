import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "sablonok"))
from _abc_adat import ADAT  # noqa: E402
from _kozos import BETOLTO, code, fejresz, md  # noqa: E402

NEV = "abc"
CIM = "ABC–XYZ-elemzés és készlethatékonyság: Pareto-görbe, besorolás, mátrix, készletforgás"

_ADAT = "[\n" + "".join(f"    ({a!r}, {b!r}, {c}, {d}),\n" for a, b, c, d in ADAT) + "]"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. kiszámítja a tételek éves felhasználási értékét, és megrajzolja a Pareto-görbét;
2. ABC-csoportokba sorolja a tételeket tételszám vagy érték szerinti határokkal, és összeveti a két besorolást;
3. a havi felhasználás relatív szórása szerint XYZ-csoportokba sorolja őket, és elkészíti az ABC–XYZ mátrixot;
4. kiszámítja a készletforgást, a készletnapokat és a készlethatékonyságot.

A beépített példa a ForgácsTech 20 anyag- és szerszámtétele (kézikönyv 21. fejezet; Silver és mtsai, 2016).
""", sablon="abc_sablon.xlsx", eszkozlap="Gyakorlati útmutató, ABC-elemzés és készlethatékonyság eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött abc_sablon.xlsx
A_TETEL, B_TETEL = 0.20, 0.60      # tételszám szerinti határok (kumulált tételarány)
A_ERTEK, B_ERTEK = 0.80, 0.95      # érték szerinti határok (kumulált értékarány)
X_CV, Y_CV = 0.5, 1.0              # XYZ-határok (a havi felhasználás relatív szórása)
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
HONAP = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "szep", "okt", "nov", "dec"]
if SAJAT_SABLON:
    fajl = sablon_betoltese("abc_sablon.xlsx")
    t = pd.read_excel(fajl, sheet_name="Tételek", header=2).iloc[:, :15]
    t.columns = ["cikk", "nev", "ar"] + HONAP
    t = t[t.cikk.notna() & pd.to_numeric(t.ar, errors="coerce").notna()].reset_index(drop=True)
    k = pd.read_excel(fajl, sheet_name="Készlethatékonyság", header=None)
    KESZLET = pd.to_numeric(k.iloc[7:19, 1], errors="coerce").dropna().to_numpy()
    MUNKANAP = float(k.iloc[4, 1])
else:
    ADAT = ''' + _ADAT + '''
    t = pd.DataFrame([(a, b, c, *d) for a, b, c, d in ADAT], columns=["cikk", "nev", "ar"] + HONAP)
    KESZLET = np.array([29.8, 32.4, 33.1, 31.0, 30.2, 29.5, 31.8, 32.6, 30.9, 30.4, 31.5, 29.6])   # MFt, hó végi
    MUNKANAP = 230
t[HONAP] = t[HONAP].apply(pd.to_numeric, errors="coerce").fillna(0)
t["menny"] = t[HONAP].sum(axis=1)
t["ertek"] = t.menny * t.ar / 1000          # eFt
t["cv"] = t[HONAP].std(axis=1, ddof=1) / t[HONAP].mean(axis=1)
print(f"{len(t)} tétel, éves felhasználás {t.ertek.sum() / 1000:.1f} MFt")
'''),
    md("## ABC- és XYZ-besorolás"),
    code('''
s = t.sort_values("ertek", ascending=False).reset_index(drop=True)
s["kum_ertek"] = s.ertek.cumsum() / s.ertek.sum()
s["kum_tetel"] = (np.arange(len(s)) + 1) / len(s)
elotte = s.kum_ertek - s.ertek / s.ertek.sum()
s["ABC_tetel"] = np.where(s.kum_tetel <= A_TETEL + 1e-9, "A", np.where(s.kum_tetel <= B_TETEL + 1e-9, "B", "C"))
s["ABC_ertek"] = np.where(elotte < A_ERTEK, "A", np.where(elotte < B_ERTEK, "B", "C"))
s["XYZ"] = np.where(s.cv <= X_CV, "X", np.where(s.cv <= Y_CV, "Y", "Z"))
for alap in ("ABC_tetel", "ABC_ertek"):
    g = s.groupby(alap).agg(tetel=("cikk", "count"), ertek=("ertek", "sum"))
    g["tetelarany"] = g.tetel / g.tetel.sum(); g["ertekarany"] = g.ertek / g.ertek.sum()
    print(f"\\n{'tételszám' if alap == 'ABC_tetel' else 'érték'} szerinti besorolás:")
    print(g.round(3).to_string())
elt = s[s.ABC_tetel != s.ABC_ertek]
print("\\nA két besorolás eltér:", ", ".join(f"{r.nev} ({r.ABC_tetel}→{r.ABC_ertek})" for r in elt.itertuples()) or "sehol")
M = pd.crosstab(s.ABC_tetel, s.XYZ).reindex(index=list("ABC"), columns=list("XYZ"), fill_value=0)
MV = s.pivot_table(index="ABC_tetel", columns="XYZ", values="ertek", aggfunc="sum").reindex(index=list("ABC"), columns=list("XYZ")).fillna(0)
print("\\nABC–XYZ mátrix (tételszám):"); print(M.to_string())
'''),
    md("## Készletforgás és készlethatékonyság"),
    code('''
atl = KESZLET.mean()
forg = t.ertek.sum() / 1000
ford = forg / atl
print(f"Átlagos készlet {atl:.1f} MFt; fordulatszám {ford:.2f}/év; készlet {365 / ford:.0f} naptári nap = {MUNKANAP / ford:.1f} munkanap; "
      f"1000 Ft forgalomra {atl / forg * 1000:.0f} Ft készlet")
# mit jelentene, ha az A tételek készletét a felére csökkentenék? (feltevés: a készlet értéke a felhasználással arányosan oszlik meg)
reszA = s.loc[s.ABC_tetel == "A", "ertek"].sum() / s.ertek.sum()
uj = atl * (1 - reszA / 2)
print(f"Ha az A tételek ({reszA:.0%} érték) készletét felezik: átlagos készlet ≈ {uj:.1f} MFt, fordulatszám ≈ {forg / uj:.2f}/év "
      "(feltevés: a készlet az éves felhasználással arányosan oszlik meg)")
'''),
    md("## Ábra"),
    code('''
szin = {"A": "#285780", "B": "#E07B39", "C": "#A9C4DE"}
fig = plt.figure(figsize=(15, 9))
ax = fig.add_axes([0.06, 0.55, 0.88, 0.40])
ax.bar(range(len(s)), s.ertek, color=[szin[g] for g in s.ABC_tetel])
ax.set_xticks(range(len(s)), s.cikk, rotation=60, fontsize=7.5, ha="right"); ax.set_ylabel("éves érték [eFt]")
ax2 = ax.twinx(); ax2.plot(range(len(s)), s.kum_ertek * 100, "o-", color="#1F3A5A", ms=3.5)
ax2.set_ylim(0, 105); ax2.set_ylabel("kumulált értékarány [%]")
for g in "ABC":
    i = np.where(s.ABC_tetel == g)[0]
    if len(i):
        ax2.text(i.mean(), 50 if g != "A" else 30, f"{g}: {len(i)} tétel, {s.ertek[i].sum() / s.ertek.sum():.0%} érték", ha="center", fontsize=9,
                 color="#1F3A5A", bbox=dict(fc="white", ec=szin[g], alpha=0.9))
ax.set_title("Pareto-diagram és ABC-csoportok (tételszám szerinti határokkal)", fontsize=10)
ax = fig.add_axes([0.06, 0.07, 0.36, 0.36])
ax.imshow(MV.to_numpy() / MV.to_numpy().sum(), cmap="Blues", vmin=0, vmax=0.8)
for i, g in enumerate("ABC"):
    for j, x in enumerate("XYZ"):
        ax.text(j, i, f"{M.loc[g, x]} tétel\\n{MV.loc[g, x] / MV.to_numpy().sum():.0%}", ha="center", va="center", fontsize=9,
                color="white" if MV.loc[g, x] / MV.to_numpy().sum() > 0.4 else "#1F3A5A")
ax.set_xticks(range(3), ["X (egyenletes)", "Y (ingadozó)", "Z (szórványos)"]); ax.set_yticks(range(3), list("ABC"))
ax.set_title("ABC–XYZ mátrix: tételszám és értékarány", fontsize=10)
ax = fig.add_axes([0.52, 0.07, 0.42, 0.36])
pelda = [s[s.XYZ == "X"].iloc[0], s[s.XYZ == "Z"].iloc[0]]
for r, c in zip(pelda, ["#285780", "#B83A3A"]):
    v = r[HONAP].to_numpy(float)
    ax.plot(range(1, 13), v / v.mean(), "o-", color=c, label=f"{r.nev} ({r.ABC_tetel}{r.XYZ}, CV = {r.cv:.2f})")
ax.axhline(1, color="#999999", ls=":"); ax.set_xticks(range(1, 13)); ax.set_xlabel("hónap"); ax.set_ylabel("havi felhasználás / havi átlag")
ax.legend(fontsize=8); ax.set_title("Egyenletes és szórványos felhasználás", fontsize=10)
plt.savefig("abc.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A 20 tétel 20%-a (három rúdanyag és a keményfém marószár) adja az éves felhasználási érték 70%-át, a következő 40% 27%-át, az utolsó 40% csupán 3%-át. Az érték szerinti határokkal (80/95%) a besorolás kissé eltér: a határon lévő tételeknél a döntést a kritikusság és a beszerzési idő is befolyásolja.
- Mind a négy A tétel egyenletes felhasználású (AX): ezekhez a rendeléshez vagy ütemtervhez kötött beszerzés és a gyakori felülvizsgálat illik. A szórványos B és C tételeknél (BZ, CZ) a rendelésre beszerzés vagy a biztonsági készlet a kérdés.
- Az átlagos készlet 31 MFt, a fordulatszám 6/év, a készlet 61 naptári, illetve 38,5 munkanapnyi felhasználás. Ha az A tételek készletét felezik, a fordulatszám jelentősen javul, mert az érték nagy része ezekben van.
"""),
]
