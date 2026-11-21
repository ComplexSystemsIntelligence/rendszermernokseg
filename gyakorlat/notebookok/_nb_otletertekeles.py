from _kozos import BETOLTO, code, fejresz, md

NEV = "otletertekeles"
CIM = "Ötletek értékelése: névleges csoport, Delphi-konvergencia, ötletmérőszámok"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. összesíti a névleges csoporttechnika csendes pontozását (pontszám, szavazatszám, rangsor, egyetértés);
2. körönként kiszámítja és ábrázolja a Delphi-becslések mediánját és interkvartilis terjedelmét;
3. kiszámítja egy ötletlista egyszerű eredményességi mérőszámait (Shah és szerzőtársai: mennyiség, változatosság, újdonság).

A beépített példa a ForgácsTech késési okainak rangsorolása és az ütemezőmodul bevezetési idejének Delphi-becslése (kézikönyv 9. fejezet).
""", sablon="otletroham_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Ötletroham és csoportos technikák eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött otletroham_sablon.xlsx
KONSZENZUS_HATAR = 0.20  # relatív interkvartilis terjedelem, amely alatt konszenzust feltételezünk
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("otletroham_sablon.xlsx")
    ngt = pd.read_excel(fajl, sheet_name="Névleges csoport", header=3).dropna(subset=["Ötlet"])
    ngt = ngt.set_index("Ötlet").filter(regex=r"^R\\d+$")
    delphi = pd.read_excel(fajl, sheet_name="Delphi", header=3)
    ures = delphi["Szakértő"].isna().to_numpy()
    delphi = delphi.iloc[:ures.argmax() if ures.any() else len(delphi)].set_index("Szakértő")
    delphi = delphi.dropna(axis=1, how="all")
    ol = pd.read_excel(fajl, sheet_name="Ötletlista", header=3)
    ol = ol[pd.to_numeric(ol["Sorszám"], errors="coerce").notna() & ol["Ötlet"].notna()]
else:
    otletek = ["sürgős rendelések szóbeli előresorolása", "alapanyag-beérkezés bizonytalansága", "váratlan gépleállások",
               "hosszú beállítási idők", "hiányos műszakátadás", "a gépállapot csak a műszak végén ismert", "szerszámhiány",
               "NC-program késése", "minőségi visszatartás", "túl optimista szállítási ígéret", "kapacitásnaptár nem naprakész",
               "betegség miatti hiányzás"]
    pont = [[5, 4, 5, 3, 5, 4, 5, 5, 4, 3, 5], [4, 5, 3, 5, 4, 3, 4, 0, 5, 4, 3], [3, 0, 4, 4, 3, 5, 2, 4, 0, 5, 4],
            [0, 3, 0, 0, 2, 0, 3, 3, 3, 0, 0], [2, 0, 0, 2, 0, 2, 0, 2, 0, 2, 2], [0, 2, 2, 0, 0, 0, 0, 0, 2, 0, 0],
            [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1], [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0], [0] * 11, [0] * 11]
    ngt = pd.DataFrame(pont, index=otletek, columns=[f"R{j + 1}" for j in range(11)]).replace(0, np.nan)
    delphi = pd.DataFrame({"1. kör": [6, 12, 8, 20, 10, 7, 9], "2. kör": [8, 10, 8, 14, 9, 8, 9], "3. kör": [8, 9, 8, 11, 9, 8, 9]},
                          index=[f"{i}. szakértő" for i in range(1, 8)])
    ol = pd.DataFrame({"Ötlet": otletek, "Kategória": ["ütemezés", "beszerzés", "gépállapot", "gépállapot", "információ",
                       "információ", "erőforrás", "technológia", "minőség", "értékesítés", "ütemezés", "erőforrás"],
                       "Újdonság (1–3)": [3, 2, 1, 1, 2, 2, 1, 1, 1, 2, 1, 1]})
'''),
    md("## Névleges csoport: összesítés"),
    code('''
er = pd.DataFrame({"pontszám": ngt.sum(axis=1, skipna=True), "szavazatok": ngt.notna().sum(axis=1),
                   "átlagpont a szavazóknál": ngt.mean(axis=1)})
er["rang"] = er["pontszám"].rank(ascending=False, method="min").astype(int)
er = er.sort_values(["pontszám", "szavazatok"], ascending=False)
reszvevo = ngt.shape[1]
er["a résztvevők hányada szavazott rá"] = (er["szavazatok"] / reszvevo).map("{:.0%}".format)
er.round(2)
'''),
    md("## Delphi: konvergencia körről körre"),
    code('''
stat = pd.DataFrame({"medián": delphi.median(), "Q1": delphi.quantile(0.25), "Q3": delphi.quantile(0.75)})
stat["IQR"] = stat["Q3"] - stat["Q1"]
stat["IQR / medián"] = stat["IQR"] / stat["medián"]
stat["konszenzus?"] = np.where(stat["IQR / medián"] <= KONSZENZUS_HATAR, "igen", "még nem")
display(stat.round(2)) if "display" in dir() else print(stat.round(2))

fig, ax = plt.subplots(figsize=(8, 4.2))
ax.boxplot([delphi[c].dropna() for c in delphi.columns], tick_labels=list(delphi.columns), widths=0.45,
           boxprops=dict(color="#285780"), medianprops=dict(color="#E07B39", lw=2))
for j, c in enumerate(delphi.columns):
    ax.scatter(np.full(delphi[c].notna().sum(), j + 1) + np.linspace(-0.12, 0.12, delphi[c].notna().sum()),
               delphi[c].dropna(), color="#4F7FAD", s=18, zorder=3)
ax.set_ylabel("becslés [hét]"); ax.grid(alpha=0.3)
ax.set_title("Delphi-becslések körönként (narancs: medián)", fontsize=10)
plt.tight_layout(); plt.savefig("delphi_konvergencia.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("## Az ötletlista mérőszámai"),
    code('''
mennyiseg = len(ol)
valtozatossag = ol["Kategória"].nunique()
ujszeru = (ol["Újdonság (1–3)"] == 3).mean() if "Újdonság (1–3)" in ol else np.nan
print(f"Mennyiség: {mennyiseg} ötlet")
print(f"Változatosság: {valtozatossag} különböző kategória (ötletek kategóriánként: {ol['Kategória'].value_counts().to_dict()})")
print(f"Újszerű (3-as) ötletek aránya: {ujszeru:.0%}")
'''),
    md("""
## Értelmezés

- A névleges csoport rangsoránál a **pontszám** mellett a **szavazatszámot** is nézd: egy ötlet, amelyre mindenki szavazott, más, mint amelyet csak ketten tettek az első helyre.
- A Delphi-módszerben a konszenzus jele az interkvartilis terjedelem csökkenése. A példában a relatív terjedelem 39%-ról 11%-ra csökkent, a medián 9 héten maradt. A szélsőséges első becslés (20 hét) szerzőjétől érdemes megkérdezni az indokot: lehet, hogy olyat tud, amit a többiek nem.
- A változatosság (hány különböző működési elv vagy kategória) a korai szakaszban fontosabb, mint a puszta mennyiség.
"""),
]
