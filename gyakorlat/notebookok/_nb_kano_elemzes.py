from _kozos import BETOLTO, code, fejresz, md

NEV = "kano_elemzes"
CIM = "Kano-elemzés Pythonban"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook Kano-kérdőív kódolt válaszait (1 = Tetszene, 2 = Elvárom, 3 = Közömbös, 4 = Elviselném,
5 = Nem tetszene) dolgozza fel:

1. a Kano-kiértékelő tábla alapján minden válaszpárt kategóriába sorol;
2. jellemzőnként összesít, és meghatározza a leggyakoribb kategóriát;
3. kiszámítja az elégedettségi együtthatókat (Berger és mtsai, 1993);
4. elkészíti az elégedettségi diagramot.

A beépített példa a kézikönyv VárosiBringa-felmérésének 120 válasza (5.5. szakasz).
""", sablon="kano_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Kano-elemzés eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött kano_sablon.xlsx feltöltése
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Kano-kiértékelő tábla: sor = funkcionális, oszlop = diszfunkcionális válasz (1..5)
TABLA = [["K", "V", "V", "V", "E"],
         ["F", "Kö", "Kö", "Kö", "A"],
         ["F", "Kö", "Kö", "Kö", "A"],
         ["F", "Kö", "Kö", "Kö", "A"],
         ["F", "F", "F", "F", "K"]]
KATEG = ["V", "E", "A", "Kö", "F", "K"]
KATNEV = {"V": "vonzó", "E": "egydimenziós", "A": "alapvető",
          "Kö": "közömbös", "F": "fordított", "K": "kétséges"}
'''),
    md("## Az adatok betöltése"),
    code('''
def peldaadat():
    """A kézikönyv példájának 120 válasza, a kategóriagyakoriságokból visszaállítva."""
    gyakorisag = {  # V, E, A, Kö, F, K
        "Megbízható zár és kölcsönzés": (6, 22, 80, 10, 0, 2),
        "Valós idejű elérhetőség az alkalmazásban": (18, 62, 28, 10, 0, 2),
        "Közös bérlet a helyi buszokkal": (58, 24, 8, 26, 2, 2),
        "Telefontöltő a kormányon": (30, 10, 4, 70, 4, 2),
        "Hangjelzés a kerékpár indulásakor": (6, 6, 4, 54, 46, 4),
    }
    par = {"V": (1, 3), "E": (1, 5), "A": (2, 5), "Kö": (3, 3), "F": (5, 3), "K": (1, 1)}
    rng = np.random.default_rng(1)
    jellemzok, oszlopok = [], {}
    for i, (nev, db) in enumerate(gyakorisag.items(), start=1):
        kod = f"J{i}"
        jellemzok.append({"Kód": kod, "Jellemző": nev})
        lista = [par[k] for k, n in zip(KATEG, db) for _ in range(n)]
        rng.shuffle(lista)
        oszlopok[f"{kod} F"] = [f for f, _ in lista]
        oszlopok[f"{kod} D"] = [d for _, d in lista]
    return pd.DataFrame(oszlopok), pd.DataFrame(jellemzok)

if SAJAT_SABLON:
    fajl = sablon_betoltese("kano_sablon.xlsx")
    valaszok = pd.read_excel(fajl, sheet_name="Válaszok", header=3)
    jellemzok = pd.read_excel(fajl, sheet_name="Jellemzők", header=3).dropna(subset=["Jellemző"])
else:
    valaszok, jellemzok = peldaadat()

kodok = [c[:-2] for c in valaszok.columns if str(c).endswith(" F")]
print("Válaszadók:", len(valaszok), "· jellemzők:", kodok)
valaszok.head()
'''),
    md("## Besorolás és elégedettségi együtthatók"),
    code('''
def kategoria(f, d):
    if pd.isna(f) or pd.isna(d):
        return None
    return TABLA[int(f) - 1][int(d) - 1]

sorok = []
for kod, nev in zip(kodok, jellemzok["Jellemző"]):
    kat = [kategoria(f, d) for f, d in zip(valaszok[f"{kod} F"], valaszok[f"{kod} D"])]
    db = pd.Series([k for k in kat if k]).value_counts()
    n = {k: int(db.get(k, 0)) for k in KATEG}
    alap = n["V"] + n["E"] + n["A"] + n["Kö"]
    sorok.append({"kód": kod, "jellemző": nev, **n,
                  "besorolás": KATNEV[max(n, key=n.get)],
                  "CS+": (n["V"] + n["E"]) / alap if alap else np.nan,
                  "CS-": -(n["E"] + n["A"]) / alap if alap else np.nan})
eredmeny = pd.DataFrame(sorok).set_index("kód")
eredmeny.round(2)
'''),
    md("## Elégedettségi diagram"),
    code('''
fig, ax = plt.subplots(figsize=(6.5, 5.5))
ax.axhline(0.5, color="#B0B8C4", lw=1); ax.axvline(0.5, color="#B0B8C4", lw=1)
ax.scatter(-eredmeny["CS-"], eredmeny["CS+"], s=70, color="#285780", zorder=3)
for kod, r in eredmeny.iterrows():
    ax.annotate(f'{kod}: {r["jellemző"]}', (-r["CS-"], r["CS+"]), textcoords="offset points",
                xytext=(6, 4), fontsize=8)
for x, y, t in [(0.97, 0.97, "egydimenziós"), (0.03, 0.97, "vonzó"),
                (0.97, 0.03, "alapvető"), (0.03, 0.03, "közömbös")]:
    ax.text(x, y, t, transform=ax.transAxes, ha="right" if x > 0.5 else "left",
            va="top" if y > 0.5 else "bottom", color="#6B7280", fontsize=9)
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_xlabel("|CS−|: a hiány okozta elégedetlenség")
ax.set_ylabel("CS+: a megléttel járó elégedettség")
ax.set_title("Elégedettségi diagram")
plt.tight_layout(); plt.show()
'''),
    md("""
## Értelmezés és továbblépés

- A **leggyakoribb kategória** csak akkor megbízható, ha jól elkülönül a második leggyakoribbtól. Közel azonos arányoknál bontsd a válaszadókat csoportokra (például használati gyakoriság szerint), és ismételd meg az elemzést csoportonként.
- Az **elégedettségi diagram** a tervezési prioritásokat segíti: az alapvető jellemzőket biztosan teljesíteni kell, az egydimenziósakban versenyképes szintre kell törekedni, a vonzó jellemzők a megkülönböztetés lehetőségei.
- Az eredményeket vidd át a minőség házába (QFD) a vevői elvárások súlyozásához.
"""),
]
