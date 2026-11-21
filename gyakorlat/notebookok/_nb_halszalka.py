import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "sablonok"))
from _gen_halszalka import KATEG, OKOK, PROBLEMA  # noqa: E402
from _kozos import BETOLTO, code, fejresz, md  # noqa: E402

NEV = "halszalka"
CIM = "Ok-okozati (halszálka-) diagram rajzolása táblázatból, az okok értékelése és igazolása"

_OKOK = "[\n" + "".join(f"    ({k!r}, {o!r}, {m!r}, {s}, {i!r}),\n" for k, o, m, s, i, *_ in OKOK) + "]"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. a lehetséges okok táblázatából (okcsoport, ok, mélyebb ok, szavazat, igazolás) automatikusan megrajzolja az ok-okozati diagramot, az igazolás állapota szerint színezve;
2. összesíti a csapat szavazatait okcsoportonként, és rangsorolja a lehetséges okokat;
3. kiemeli, mely okokat igazolták adatokkal, és melyek vizsgálandók még.

A beépített példa a ForgácsTech anyagra várási problémája (kézikönyv 25. fejezet; Ishikawa, 1982; NASA RP-1358, 7.2).
""", sablon="halszalka_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Ok-okozati diagram eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött halszalka_sablon.xlsx
''' + BETOLTO + '''
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("halszalka_sablon.xlsx")
    PROBLEMA = str(pd.read_excel(fajl, sheet_name="Okok", header=None, nrows=4).iloc[3, 1])
    okok = pd.read_excel(fajl, sheet_name="Okok", header=4).iloc[:40, :5]
    okok.columns = ["csoport", "ok", "mely", "szavazat", "igazolas"]
    okok = okok[okok.csoport.notna() & okok.ok.notna()].reset_index(drop=True)
    KATEG = [k for k in pd.read_excel(fajl, sheet_name="Csoportok", header=3).iloc[:8, 0].dropna()]
else:
    PROBLEMA = ''' + repr(PROBLEMA) + '''
    KATEG = ''' + repr(KATEG) + '''
    okok = pd.DataFrame(''' + _OKOK + ''', columns=["csoport", "ok", "mely", "szavazat", "igazolas"])
okok["szavazat"] = pd.to_numeric(okok.szavazat, errors="coerce").fillna(0)
okok["igazolas"] = okok.igazolas.fillna("vizsgálandó")
print(PROBLEMA); print(f"{len(okok)} lehetséges ok, {okok.csoport.nunique()} okcsoport")
'''),
    md("## Összesítés és rangsor"),
    code('''
cs = okok.groupby("csoport").agg(okok=("ok", "size"), szavazat=("szavazat", "sum")).reindex(KATEG).fillna(0)
cs["igazolt"] = okok[okok.igazolas == "igazolt"].groupby("csoport").size().reindex(KATEG).fillna(0)
print(cs.astype(int).to_string())
print("\\nA legtöbb szavazatot kapott okok:")
print(okok.sort_values("szavazat", ascending=False).head(6)[["csoport", "ok", "szavazat", "igazolas"]].to_string(index=False))
print("\\nIgazolt okok:", "; ".join(okok.loc[okok.igazolas == "igazolt", "ok"]))
print("Vizsgálandó okok:", "; ".join(okok.loc[okok.igazolas == "vizsgálandó", "ok"]))
'''),
    md("""## A diagram rajzolása

A gerinc balról jobbra a problémához (fejhez) vezet; a csontok az okcsoportok, rajtuk a lehetséges okok. Zöld: adatokkal igazolt ok, szürke: elvetett, sötét: még vizsgálandó."""),
    code('''
SZIN = {"igazolt": "#3E8E63", "elvetett": "#9AA1AB", "vizsgálandó": "#1F2933"}
fent, lent = KATEG[:3], KATEG[3:6]
fig, ax = plt.subplots(figsize=(16, 7.5))
L, H = 15.0, 3.4
ax.annotate("", xy=(L, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", lw=2.5, color="#1B3A57", mutation_scale=22))
ax.text(L + 0.2, 0, "\\n".join(textwrap.wrap(PROBLEMA, 24)), va="center", ha="left", fontsize=10, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.5", fc="#FBE7D9", ec="#E07B39", lw=1.5))
for sor, (csoportok, irany) in enumerate([(fent, 1), (lent, -1)]):
    for j, k in enumerate(csoportok):
        x0 = 3.6 + j * 4.6           # a csont talppontja a gerincen
        xt, yt = x0 - 2.2, irany * H  # a csont vége
        ax.plot([xt, x0], [yt, 0], color="#1B3A57", lw=1.6)
        ax.text(xt, yt + irany * 0.35, k, ha="center", va="center", fontsize=10, color="white", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.35", fc="#285780", ec="#1B3A57"))
        sorok = okok[okok.csoport == k].reset_index(drop=True)
        for i, s in sorok.iterrows():
            frac = (i + 1) / (len(sorok) + 1)
            y = irany * H * (1 - frac)
            xb = x0 - 2.2 * (abs(y) / H)
            ax.plot([xb - 0.35, xb], [y, y], color="#9AA1AB", lw=0.8)
            felirat = "\\n".join(textwrap.wrap(f"{s.ok} ({int(s.szavazat)})", 30))
            ax.text(xb - 0.4, y, felirat, ha="right", va="center", fontsize=8, color=SZIN.get(s.igazolas, "#1F2933"),
                    fontweight="bold" if s.igazolas == "igazolt" else "normal")
ax.set_xlim(-2.6, L + 3.4); ax.set_ylim(-H - 1.0, H + 1.0); ax.axis("off")
ax.set_title("Ok-okozati diagram (zárójelben a csapat szavazatai; zöld: igazolt, szürke: elvetett)", fontsize=11)
plt.tight_layout(); plt.savefig("halszalka.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""## Értelmezés

- A szavazás a csapat véleményét rögzíti, nem a valóságot: a ForgácsTech példájában a „darabolás szűk keresztmetszet” három szavazatot kapott, de az adatok (52%-os kihasználtság) elvetették.
- A módszer csoport kapta a legtöbb szavazatot, és ott van a három igazolt ok is: a gyökérokot az 5 miért elemzés a folyamatok összekötésének hiányára vezette vissza.
- A vizsgálandó okokat nem szabad elfelejteni: ha az intézkedés után a probléma nem szűnik meg, ezek a következő jelöltek.
"""),
]
