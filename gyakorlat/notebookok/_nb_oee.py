from _kozos import BETOLTO, code, fejresz, md

NEV = "oee"
CIM = "OEE: műszakonkénti A, P, Q, a hat nagy veszteség, vízesés, a beállításiidő-csökkentés hatása és az OLE"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. műszakonként és az időszakra kiszámítja a rendelkezésre állást (A), a teljesítményt (P), a minőséget (Q) és az OEE-t (az időszaki értéket az összegekből);
2. percben kimutatja a hat nagy veszteséget, és megrajzolja az OEE-vízesést;
3. megvizsgálja, mennyire szóródik az OEE a műszakok között, és melyik tényező felel a szórásért;
4. kiszámítja, hogyan változik az OEE és a sorozatnagyság, ha a beállítási idő csökken (SMED);
5. a munkára is kiszámítja a hatékonyságot (OLE).

A beépített példa a ForgácsTech megmunkáló központja 20 műszakon át, az OLE-példa a VárosiBringa javítóműhelye (kézikönyv 19. fejezet; Nakajima, 1988; Muchiri és Pintelon, 2008; Braglia és mtsai, 2021).
""", sablon="oee_sablon.xlsx", eszkozlap="Gyakorlati útmutató, OEE-számítás eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött oee_sablon.xlsx
SMED_IDO = 8           # az átállás tervezett ideje SMED után [perc]
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
OSZL = ["muszak", "terv", "atall_db", "atall", "meghib", "kisebb", "gyartott", "jo", "inditasi"]
if SAJAT_SABLON:
    fajl = sablon_betoltese("oee_sablon.xlsx")
    p = pd.read_excel(fajl, sheet_name="Adatok", header=None, nrows=4)
    TI = float(p.iloc[3, 1])
    d = pd.read_excel(fajl, sheet_name="Adatok", header=6).iloc[:, :9]
    d.columns = OSZL
    d = d[pd.to_numeric(d.terv, errors="coerce").notna() & pd.to_numeric(d.gyartott, errors="coerce").notna()]
    d = d[d.muszak.astype(str) != "Összesen"].reset_index(drop=True)
    ole = pd.read_excel(fajl, sheet_name="OLE", header=2).iloc[:, :6]
    ole.columns = ["dolgozo", "terv", "nem_rend", "normaido", "munkak", "jo"]
    ole = ole[ole.dolgozo.notna() & (ole.dolgozo != "Összesen") & pd.to_numeric(ole.terv, errors="coerce").notna()]
else:
    TI = 4.0
    d = pd.DataFrame([
        (1, 450, 2, 93, 55, 26, 62, 59, 3), (2, 450, 2, 91, 0, 20, 76, 72, 2), (3, 450, 1, 51, 0, 25, 84, 79, 1),
        (4, 450, 2, 95, 0, 28, 73, 69, 1), (5, 450, 2, 103, 30, 21, 66, 62, 0), (6, 450, 2, 78, 69, 17, 64, 63, 0),
        (7, 450, 2, 112, 0, 24, 70, 68, 0), (8, 450, 2, 95, 0, 23, 74, 69, 3), (9, 450, 2, 103, 0, 29, 71, 64, 1),
        (10, 450, 1, 47, 0, 14, 87, 81, 0), (11, 450, 2, 92, 103, 18, 53, 49, 3), (12, 450, 2, 101, 0, 17, 74, 71, 1),
        (13, 450, 2, 104, 0, 12, 75, 73, 0), (14, 450, 2, 94, 25, 23, 69, 64, 2), (15, 450, 2, 94, 75, 25, 57, 53, 4),
        (16, 450, 3, 154, 43, 18, 52, 52, 0), (17, 450, 2, 87, 0, 30, 74, 68, 3), (18, 450, 3, 121, 0, 27, 67, 64, 1),
        (19, 450, 2, 100, 0, 26, 72, 63, 4), (20, 450, 2, 105, 0, 17, 80, 77, 1)], columns=OSZL)
    ole = pd.DataFrame([("1. szerelő", 450, 45, 340, 20, 19), ("2. szerelő", 450, 30, 372, 22, 22), ("3. szerelő", 450, 60, 318, 18, 16)],
                       columns=["dolgozo", "terv", "nem_rend", "normaido", "munkak", "jo"])
for c in OSZL[1:]:
    d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
d["mukodes"] = d.terv - d.atall - d.meghib
d["idealis"] = d.gyartott * TI
d["A"] = d.mukodes / d.terv; d["P"] = d.idealis / d.mukodes; d["Q"] = d.jo / d.gyartott; d["OEE"] = d.A * d.P * d.Q
d["sebesseg"] = d.mukodes - d.kisebb - d.idealis
d["folyamatselejt"] = d.gyartott - d.jo - d.inditasi
assert (d.sebesseg >= -1e-9).all(), "Negatív sebességveszteség: az ideális ciklusidő vagy a darabszám hibás"
S = d[OSZL[1:] + ["mukodes", "idealis", "sebesseg", "folyamatselejt"]].sum()
A, P, Q = S.mukodes / S.terv, S.idealis / S.mukodes, S.jo / S.gyartott
OEE = A * P * Q
print(f"{len(d)} műszak: A = {A:.3f}, P = {P:.3f}, Q = {Q:.3f}, OEE = {OEE:.3f} (ellenőrzés: jó darabok ideális ideje / tervezett idő = {S.jo * TI / S.terv:.3f})")
print(f"A műszakonkénti OEE átlaga {d.OEE.mean():.3f}, terjedelme {d.OEE.min():.3f}–{d.OEE.max():.3f}; "
      "az arányok átlaga eltérhet az összegekből számolt értéktől.")
'''),
    md("## A hat nagy veszteség és a szórás okai"),
    code('''
n = len(d)
vesz = pd.Series({
    "1. meghibásodás": S.meghib, "2. beállítás, átállás": S.atall, "3. kisebb leállások": S.kisebb,
    "4. csökkentett sebesség": S.sebesseg, "5. selejt, utómunka": S.folyamatselejt * TI, "6. indítási veszteség": S.inditasi * TI}) / n
ertekes = S.jo * TI / n
print("Egy műszakra jutó veszteség [perc]:"); print(vesz.round(1).to_string())
print(f"értékes idő: {ertekes:.1f} perc; összesen {vesz.sum() + ertekes:.1f} perc (tervezett: {S.terv / n:.1f})")
# melyik tényező magyarázza az OEE műszakok közötti szórását? (log-felbontás: ln OEE = ln A + ln P + ln Q)
L = np.log(d[["A", "P", "Q"]])
kov = L.cov()
var_oee = np.log(d.OEE).var()
hozz = {k: (kov.loc[k].sum()) / var_oee for k in ["A", "P", "Q"]}
print("Az ln OEE szórásnégyzetéhez való hozzájárulás:", {k: f"{v:.0%}" for k, v in hozz.items()})
print("Az átállások száma és az OEE korrelációja:", round(float(np.corrcoef(d.atall_db, d.OEE)[0, 1]), 2))
'''),
    md("## SMED: rövidebb átállás, kisebb sorozatok"),
    code('''
T, M = S.terv / n, S.meghib / n
c0 = S.atall_db / n; t0 = S.atall / S.atall_db
print(f"Jelenleg {c0:.1f} átállás műszakonként, átlagosan {t0:.0f} perc")
eredm = []
for c in (1, 2, 4, 8):
    for t in (t0, 19, 11, SMED_IDO):
        a = (T - c * t - M) / T
        eredm.append(dict(atallas=c, ido=t, A=a, OEE=a * P * Q, sorozat=c0 / c))
E = pd.DataFrame(eredm)
print(E.pivot(index="atallas", columns="ido", values="OEE").round(3).to_string())
print("A sorozatnagyság és a gép előtti készlet a jelenlegihez képest (Little-törvény, változatlan áram mellett):",
      {c: round(float(c0 / c), 2) for c in (1, 2, 4, 8)})
'''),
    md("## OLE: a munka hatékonysága"),
    code('''
for c in ["terv", "nem_rend", "normaido", "munkak", "jo"]:
    ole[c] = pd.to_numeric(ole[c], errors="coerce")
ole["A"] = (ole.terv - ole.nem_rend) / ole.terv
ole["P"] = ole.normaido / (ole.terv - ole.nem_rend)
ole["Q"] = ole.jo / ole.munkak
ole["OLE"] = ole.A * ole.P * ole.Q
o = ole.sum(numeric_only=True)
print(ole[["dolgozo", "A", "P", "Q", "OLE"]].round(3).to_string(index=False))
print(f"Összesen: A = {(o.terv - o.nem_rend) / o.terv:.3f}, P = {o.normaido / (o.terv - o.nem_rend):.3f}, Q = {o.jo / o.munkak:.3f}, "
      f"OLE = {(o.terv - o.nem_rend) / o.terv * o.normaido / (o.terv - o.nem_rend) * o.jo / o.munkak:.3f}")
'''),
    md("## Ábra"),
    code('''
fig, axs = plt.subplots(2, 2, figsize=(14, 9))
ax = axs[0, 0]
lepcs = [("tervezett", T, 0, "#285780"), ("átállás", vesz.iloc[1], T - vesz.iloc[1], "#B83A3A"),
         ("meghibásodás", vesz.iloc[0], T - vesz.iloc[1] - vesz.iloc[0], "#B83A3A")]
mk = T - vesz.iloc[0] - vesz.iloc[1]
lepcs += [("működési", mk, 0, "#4F7FAF"), ("sebesség", vesz.iloc[2] + vesz.iloc[3], mk - vesz.iloc[2] - vesz.iloc[3], "#E07B39")]
nt = mk - vesz.iloc[2] - vesz.iloc[3]
lepcs += [("nettó", nt, 0, "#4F7FAF"), ("minőség", vesz.iloc[4] + vesz.iloc[5], nt - vesz.iloc[4] - vesz.iloc[5], "#E07B39"),
          ("értékes", ertekes, 0, "#3E8E63")]
for i, (nev, h, b, c) in enumerate(lepcs):
    ax.bar(i, h, bottom=b, color=c)
    ax.text(i, b + h + 4, f"{h:.0f}", ha="center", fontsize=8)
ax.set_xticks(range(len(lepcs)), [l[0] for l in lepcs], fontsize=8, rotation=20)
ax.set_ylabel("perc / műszak"); ax.set_title(f"OEE-vízesés: A {A:.3f} · P {P:.3f} · Q {Q:.3f} = {OEE:.3f}", fontsize=10)
ax = axs[0, 1]
for k, c in (("A", "#285780"), ("P", "#E07B39"), ("Q", "#3E8E63"), ("OEE", "#1F1F1F")):
    ax.plot(d.index + 1, d[k] * 100, "o-" if k == "OEE" else "-", color=c, label=k, lw=2 if k == "OEE" else 1.2, ms=4)
ax.axhline(OEE * 100, color="#999999", ls=":"); ax.set_ylim(0, 105)
ax.set_xticks(range(1, len(d) + 1, max(1, len(d) // 10))); ax.set_xlabel("műszak"); ax.set_ylabel("%"); ax.legend(fontsize=8, ncol=4, loc="lower right"); ax.set_title("Műszakonkénti értékek", fontsize=10)
ax.grid(alpha=0.3)
ax = axs[1, 0]
vs = vesz.sort_values()
ax.barh(vs.index, vs.values, color=["#B83A3A" if i.startswith(("1", "2")) else "#E07B39" for i in vs.index])
ax.set_xlabel("perc / műszak"); ax.set_title("A hat nagy veszteség", fontsize=10)
ax = axs[1, 1]
for t, st in ((t0, "-"), (19, "--"), (11, "-."), (SMED_IDO, ":")):
    e = E[E.ido == t]
    ax.plot(e.atallas, e.OEE * 100, st, marker="o", label=f"átállás {t:.0f} perc", color="#285780")
ax.scatter([c0], [OEE * 100], s=90, color="#B83A3A", zorder=5); ax.text(c0 + 0.15, OEE * 100 - 3, "jelenlegi", fontsize=8, color="#B83A3A")
ax.set_xscale("log", base=2); ax.set_xticks([1, 2, 4, 8], ["1", "2", "4", "8"])
ax.set_xlabel("átállások száma műszakonként (fordítottan arányos a sorozatnagysággal)"); ax.set_ylabel("OEE [%]")
ax.legend(fontsize=8); ax.set_title("SMED: átállási idő és sorozatnagyság", fontsize=10); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("oee.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A megmunkáló központ OEE-je 0,587 (A 0,742, P 0,838, Q 0,943): a tervezett üzemidőnek csak 59%-a jelent jó terméket. A legnagyobb veszteség a beállítás (96 perc műszakonként), ezt a sebességveszteségek (54 perc) és a meghibásodás (20 perc) követik.
- A műszakok közötti szórást főleg a rendelkezésre állás okozza: a három átállásos és a meghibásodásos műszakok OEE-je a legkisebb.
- 8 perces átállással és változatlan sorozatnagysággal az OEE 0,727-re nőne. Ha a sorozatokat felezik (négy átállás műszakonként), az OEE 0,699, a gép előtti készlet és várakozás pedig a felére csökken. A ForgácsTech ezt a változatot választotta, mert a célja a határidő-tartás és az átfutás csökkentése.
- Az OLE-példában a második szerelő hatékonysága a legnagyobb; a harmadiknál a várakozás és az utómunka is nagyobb. Az eltérés okát a munkaszervezésben (alkatrész-ellátás, betanítás) kell keresni.
"""),
]
