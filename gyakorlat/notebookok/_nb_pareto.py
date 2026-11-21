import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "sablonok"))
from _allasido_adat import ADAT  # noqa: E402
from _kozos import BETOLTO, code, fejresz, md  # noqa: E402

NEV = "pareto"
CIM = "Pareto-diagram és rétegzés: okok rangsora időtartam, gyakoriság és költség szerint, előtte–utána összevetés"

_ADAT = "[\n" + "".join(f"    ({a!r}, {b!r}, {c!r}, {d}),\n" for a, b, c, d in ADAT) + "]"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. eseménynaplóból (ellenőrzőlapból) Pareto-diagramot készít időtartam, gyakoriság és (opcionálisan) költség szerint, és megmutatja, hogy a rangsor a mértéktől függ;
2. rétegzi az adatokat (gép × ok), és rétegenként is rangsorol;
3. egy fejlesztés előtti és utáni időszakot összevet.

A beépített példa a ForgácsTech egy havi állásidő-naplója a MES bevezetése után (kézikönyv 25. fejezet; Ishikawa, 1982; Montgomery, 2020; NASA RP-1358, 5.5–5.6).
""", sablon="pareto_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Pareto-diagram eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött pareto_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("pareto_sablon.xlsx")
    naplo = pd.read_excel(fajl, sheet_name="Napló", header=3).iloc[:400, :4]
    naplo.columns = ["datum", "reteg", "ok", "perc"]
    naplo = naplo[naplo.ok.notna()].reset_index(drop=True)
    okok = pd.read_excel(fajl, sheet_name="Okok", header=3).iloc[:15, :2]
    okok.columns = ["ok", "suly"]; okok = okok[okok.ok.notna()]
    SULY = {o: (float(s) if pd.notna(s) else 1.0) for o, s in zip(okok.ok, okok.suly)}
else:
    ADAT = ''' + _ADAT + '''
    naplo = pd.DataFrame(ADAT, columns=["datum", "reteg", "ok", "perc"])
    SULY = {}
naplo["perc"] = pd.to_numeric(naplo.perc, errors="coerce").fillna(0)
naplo["hatas"] = naplo.perc * naplo.ok.map(SULY).fillna(1.0)
print(f"{len(naplo)} esemény, {naplo.perc.sum():.0f} perc, {naplo.ok.nunique()} ok, {naplo.reteg.nunique()} réteg")
'''),
    md("## Pareto-táblázat"),
    code('''
def pareto(s):
    s = s.sort_values(ascending=False)
    t = pd.DataFrame({"hatás": s, "arány": s / s.sum()})
    t["kumulált"] = t["arány"].cumsum()
    t["osztály"] = np.where(t["kumulált"] - t["arány"] < 0.8 - 1e-9, "A", "B")
    return t

P_ido = pareto(naplo.groupby("ok").hatas.sum())
P_db = pareto(naplo.groupby("ok").size().astype(float))
print("Időtartam (súlyozott hatás) szerint:"); print(P_ido.round(3).to_string())
print("\\nGyakoriság szerint:"); print(P_db.round(3).to_string())
elt = [o for o in P_ido.index if list(P_ido.index).index(o) != list(P_db.index).index(o)]
print(f"\\nA rangsor a mértéktől függ: {len(elt)} ok helye változik.")
'''),
    md("## Rétegzés"),
    code('''
R = naplo.pivot_table(index="ok", columns="reteg", values="hatas", aggfunc="sum", fill_value=0).loc[P_ido.index]
print(R.astype(int).to_string())
for ok in P_ido.index[:2]:
    sor = R.loc[ok]
    print(f"{ok}: a legnagyobb rétegek {', '.join(f'{k} ({v / sor.sum():.0%})' for k, v in sor.sort_values(ascending=False).head(3).items())}")
'''),
    md("""## Előtte–utána

A fejlesztés hatását ugyanazzal a mértékkel, azonos hosszúságú időszakra mérjük. A beépített példában a DMAIC-projekt után az anyagra várás havi 1120 percről 380 percre csökkent (kézikönyv 25. fejezet); a többi ok változatlan. A fejlesztés után a Pareto-sorrend megváltozik: a következő fejlesztés célpontja az új első ok."""),
    code('''
if SAJAT_SABLON:
    osszevet = None
    print("Saját adatnál a fejlesztés utáni időszak naplóját külön sablonban rögzítsd, és futtasd újra a notebookot; "
          "az ábra harmadik része itt a gyakoriság szerinti rangsort mutatja.")
else:
    utana = naplo.groupby("ok").hatas.sum().copy()
    utana["anyagra várás"] = 380
    P_utana = pareto(utana)
    osszevet = pd.DataFrame({"előtte": naplo.groupby("ok").hatas.sum(), "utána": utana}).loc[P_ido.index]
    print(osszevet.astype(int).to_string())
    print(f"\\nÖsszes: {osszevet['előtte'].sum():.0f} → {osszevet['utána'].sum():.0f}; az új első ok: {P_utana.index[0]}")
'''),
    md("## Ábra"),
    code('''
fig, ax = plt.subplots(1, 3, figsize=(17, 5), gridspec_kw={"width_ratios": [1.25, 1, 1]})
x = np.arange(len(P_ido))
ax[0].bar(x, P_ido["hatás"], color=["#285780" if o == "A" else "#A9C4DE" for o in P_ido["osztály"]])
ax[0].set_xticks(x); ax[0].set_xticklabels(P_ido.index, rotation=35, ha="right", fontsize=8)
ax[0].set_ylabel("hatás (perc)"); ax[0].set_ylim(0, P_ido["hatás"].sum())
a2 = ax[0].twinx(); a2.plot(x, 100 * P_ido["kumulált"], "o-", color="#E07B39"); a2.set_ylim(0, 100); a2.set_ylabel("kumulált arány [%]")
a2.axhline(80, color="#E07B39", ls="--", lw=0.8)
ax[0].set_title("Pareto-diagram"); ax[0].spines[["top"]].set_visible(False)

im = ax[1].imshow(R.to_numpy(), cmap="Blues", aspect="auto")
ax[1].set_xticks(range(R.shape[1])); ax[1].set_xticklabels(R.columns, fontsize=8)
ax[1].set_yticks(range(R.shape[0])); ax[1].set_yticklabels(R.index, fontsize=8)
for i in range(R.shape[0]):
    for j in range(R.shape[1]):
        v = R.iat[i, j]
        if v: ax[1].text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7, color="white" if v > R.to_numpy().max() * 0.55 else "#1F2933")
ax[1].set_title("Rétegzés: ok × réteg")

if osszevet is not None:
    y = np.arange(len(osszevet))
    ax[2].barh(y - 0.2, osszevet["előtte"], height=0.4, color="#A9C4DE", label="előtte")
    ax[2].barh(y + 0.2, osszevet["utána"], height=0.4, color="#285780", label="utána")
    ax[2].set_yticks(y); ax[2].set_yticklabels(osszevet.index, fontsize=8)
    ax[2].set_xlabel("perc/hó"); ax[2].legend(frameon=False, fontsize=8); ax[2].set_title("Előtte–utána")
else:
    y = np.arange(len(P_db))
    ax[2].barh(y, P_db["hatás"], color="#285780"); ax[2].set_yticks(y); ax[2].set_yticklabels(P_db.index, fontsize=8)
    ax[2].set_xlabel("események száma"); ax[2].set_title("Gyakoriság szerint")
ax[2].invert_yaxis()
ax[2].spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig("pareto.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""## Értelmezés

- Időtartam szerint az első három ok az állásidő 69%-a; ezekre érdemes összpontosítani.
- Gyakoriság szerint más a sorrend: a rövid, gyakori események (szerszámcsere, kezelőre várás) előrébb kerülnek. A mértéket a cél határozza meg (rendelkezésre állás: idő; zavarás: gyakoriság; költség: súlyozott hatás).
- A rétegzés szerint az anyagra várás túlnyomóan a megmunkáló központokat érinti, ahol a rendelések átsorolása gyakori; az átállás az esztergákon jelentős.
- A fejlesztés után a Pareto-sorrend megváltozik; a folyamatos fejlesztésben a Pareto-elemzést rendszeresen meg kell ismételni.
"""),
]
