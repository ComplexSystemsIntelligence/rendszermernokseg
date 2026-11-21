from _kozos import BETOLTO, code, fejresz, md

NEV = "erdekelt_felek"
CIM = "Érdekelt felek priorizálása: hatalom–érdekeltség rács és fontossági modell"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook egy érdekeltfél-nyilvántartásból (hatalom és érdekeltség 1–5 skálán, legitim és sürgős követelés 0/1)

1. meghatározza a hatalom–érdekeltség rács negyedét (Mendelow, 1981; Eden és Ackermann, 1998);
2. besorolja az érdekelt feleket a fontossági modell osztályaiba (Mitchell, Agle és Wood, 1997);
3. felrajzolja a rácsot, és bevonási javaslatot ad.

A beépített példa a kézikönyv VárosiBringa-esetének 12 érdekelt fele (5.3. szakasz).
""", sablon="erdekelt_felek_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Hatalom–érdekeltség és fontossági elemzés eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött erdekelt_felek_sablon.xlsx feltöltése
KUSZOB = 3             # a negyedek határa a pontskálán
''' + BETOLTO + '''
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## A nyilvántartás betöltése"),
    code('''
PELDA = [
    ("Önkormányzat", 5.0, 4.8, 1, 1), ("Üzemeltető konzorcium", 4.3, 4.6, 1, 1),
    ("Közlekedési társaság", 3.6, 3.3, 1, 0), ("Egyetem", 3.2, 3.9, 1, 0),
    ("Diák felhasználók", 1.9, 4.5, 1, 1), ("Akadálymentességi érdekképviselet", 1.6, 4.1, 1, 1),
    ("Környezetvédő civilek", 1.25, 3.45, 1, 0), ("Gyalogosok, boltosok", 1.7, 2.6, 1, 0),
    ("Helyi média", 2.3, 1.6, 0, 0), ("Energiaszolgáltató", 3.4, 1.4, 1, 0),
    ("Közlekedési hatóság", 4.5, 1.9, 1, 0), ("Rendőrség", 3.5, 2.1, 1, 0),
]
if SAJAT_SABLON:
    fajl = sablon_betoltese("erdekelt_felek_sablon.xlsx")
    ny = pd.read_excel(fajl, sheet_name="Nyilvántartás", header=3)
    ny = ny.rename(columns={"Érdekelt fél": "nev", "Hatalom (1–5)": "H", "Érdekeltség (1–5)": "E",
                            "Legitim követelés? (1/0)": "L", "Sürgős? (1/0)": "S"})
    ny = ny.dropna(subset=["nev", "H", "E"])[["nev", "H", "E", "L", "S"]]
else:
    ny = pd.DataFrame(PELDA, columns=["nev", "H", "E", "L", "S"])
ny
'''),
    md("## Negyed, fontossági osztály, bevonás"),
    code('''
OSZTALY = {(0, 0, 0): "nem érdekelt", (0, 0, 1): "követelőző", (0, 1, 0): "mérlegelhető", (0, 1, 1): "függő",
           (1, 0, 0): "szunnyadó", (1, 0, 1): "veszélyes", (1, 1, 0): "domináns", (1, 1, 1): "meghatározó"}
BEVONAS = {"kulcsszereplő": "szoros együttműködés, közös döntés", "érintett": "tájékoztatás és bevonás",
           "keretadó": "elégedettség fenntartása", "tömeg": "figyelemmel kísérés"}

def negyed(h, e):
    if h >= KUSZOB and e >= KUSZOB: return "kulcsszereplő"
    if e >= KUSZOB: return "érintett"
    if h >= KUSZOB: return "keretadó"
    return "tömeg"

ny["negyed"] = [negyed(h, e) for h, e in zip(ny["H"], ny["E"])]
ny["fontossági osztály"] = [OSZTALY[(int(h >= KUSZOB), int(l), int(s))] for h, l, s in zip(ny["H"], ny["L"], ny["S"])]
ny["javasolt bevonás"] = ny["negyed"].map(BEVONAS)
ny.sort_values(["negyed", "H"], ascending=[True, False])
'''),
    md("## A hatalom–érdekeltség rács"),
    code('''
SZIN = {"kulcsszereplő": "#E07B39", "érintett": "#3E8E63", "keretadó": "#285780", "tömeg": "#6B7280"}
fig, ax = plt.subplots(figsize=(8, 7))
ax.axhline(KUSZOB, color="#B0B8C4"); ax.axvline(KUSZOB, color="#B0B8C4")
for _, r in ny.iterrows():
    ax.scatter(r["E"], r["H"], s=80, color=SZIN[r["negyed"]], zorder=3)
    ax.annotate(r["nev"], (r["E"], r["H"]), xytext=(6, 4), textcoords="offset points", fontsize=8)
for (x, y, t) in [(4.95, 5.05, "kulcsszereplők"), (4.95, 0.95, "érintettek"),
                  (1.05, 5.05, "keretadók"), (1.05, 0.95, "tömeg")]:
    ax.text(x, y, t, ha="right" if x > 3 else "left", va="top" if y > 3 else "bottom", color="#6B7280")
ax.set_xlim(0.8, 5.2); ax.set_ylim(0.8, 5.2)
ax.set_xlabel("érdekeltség"); ax.set_ylabel("hatalom")
ax.set_title("Hatalom–érdekeltség rács")
plt.tight_layout(); plt.savefig("hatalom_erdekeltseg.png", bbox_inches="tight"); plt.show()
'''),
    md("""
## Értelmezés

- A rács **pillanatfelvétel**. Gondold végig, ki léphet át egy másik negyedbe (szövetség, hatósági eljárás, sajtóhír), és vedd fel ezt a kockázatlistára.
- A **függő** érdekeltek (legitim és sürgős követelés, kis hatalom) könnyen meghatározóvá válhatnak, ha szövetségest találnak. Érdemes őket korán bevonni.
- A pontszámok szubjektívek: a csapattagok független pontozása és az eltérések megbeszélése után töltsd ki a sablont.
"""),
]
