from _kozos import BETOLTO, code, fejresz, md

NEV = "kontextusdiagram"
CIM = "Kontextusdiagram az interfészlistából"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook egy interfészlistából (külső entitás, kölcsönhatás, irány, típus) automatikusan felrajzolja
a rendszer kontextusdiagramját, és elvégzi a táblázatos ellenőrzéseket:

1. hiányzó irány vagy típus, túl általános címke;
2. csak bemenettel vagy csak kimenettel rendelkező entitások;
3. a kölcsönhatások megoszlása típus és irány szerint.

A beépített példa a VárosiBringa közösségi kerékpár-szolgáltatás interfészlistája.
""", sablon="kontextusdiagram_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Kontextusdiagram eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött kontextusdiagram_sablon.xlsx feltöltése
RENDSZER = "VárosiBringa\\nközösségi kerékpár-\\nszolgáltatás"   # a középső alakzat felirata
''' + BETOLTO + '''
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch
'''),
    md("## Az interfészlista betöltése"),
    code('''
PELDA = [
    ("Felhasználók", "kölcsönzési kérés", "be", "adat"),
    ("Felhasználók", "visszaigazolás, díj", "ki", "adat"),
    ("Felhasználók", "feltöltött kerékpár", "ki", "anyag"),
    ("Felhasználók", "visszahozott kerékpár", "be", "anyag"),
    ("Felhasználók", "hibabejelentés", "be", "adat"),
    ("Fizetési szolgáltató", "fizetési kérelem", "ki", "adat"),
    ("Fizetési szolgáltató", "fizetési visszaigazolás", "be", "adat"),
    ("Helyi közlekedési társaság", "érvényes bérletek", "be", "adat"),
    ("Helyi közlekedési társaság", "közös bérlet elszámolása", "ki", "adat"),
    ("Önkormányzat", "közterület-használati engedély", "be", "adat"),
    ("Önkormányzat", "használati jelentés", "ki", "adat"),
    ("Energiaszolgáltató", "villamos energia", "be", "energia"),
    ("Navigációs szolgáltatók", "állomás- és készletadatok", "ki", "adat"),
    ("Rendőrség", "lopásbejelentés", "ki", "adat"),
    ("Kerékpár-beszállító", "pótalkatrész-rendelés", "ki", "adat"),
    ("Kerékpár-beszállító", "pótalkatrész, javítás", "be", "anyag"),
    ("Akkumulátor-újrahasznosító", "elhasznált akkumulátor", "ki", "anyag"),
]

if SAJAT_SABLON:
    fajl = sablon_betoltese("kontextusdiagram_sablon.xlsx")
    df = pd.read_excel(fajl, sheet_name="Interfészlista", header=3)
    df = df.rename(columns={"Külső entitás": "entitas", "Kölcsönhatás (mi megy át a határon?)": "kolcsonhatas",
                            "Irány (be/ki)": "irany", "Típus": "tipus"})
    df = df.dropna(subset=["entitas"])[["entitas", "kolcsonhatas", "irany", "tipus"]]
else:
    df = pd.DataFrame(PELDA, columns=["entitas", "kolcsonhatas", "irany", "tipus"])
df["irany"] = df["irany"].str.strip().str.lower()
df["tipus"] = df["tipus"].str.strip().str.lower()
df
'''),
    md("## Ellenőrzések"),
    code('''
ALTALANOS = {"adat", "adatok", "információ", "kommunikáció", "adatcsere"}
gond = df[df["irany"].isna() | df["tipus"].isna() | df["kolcsonhatas"].str.lower().str.strip().isin(ALTALANOS)]
print("Hiányos vagy túl általános sorok:", "nincs" if gond.empty else "")
if not gond.empty:
    display(gond)

osszes = df.pivot_table(index="entitas", columns="irany", values="kolcsonhatas", aggfunc="count", fill_value=0)
for oszlop in ("be", "ki"):
    if oszlop not in osszes:
        osszes[oszlop] = 0
osszes["megjegyzés"] = np.where(osszes["be"] == 0, "csak kimenet – rendben?",
                        np.where(osszes["ki"] == 0, "csak bemenet – rendben?", ""))
display(osszes)
display(pd.crosstab(df["tipus"], df["irany"], margins=True, margins_name="összesen"))
'''),
    md("## A kontextusdiagram felrajzolása"),
    code('''
SZIN = {"adat": "#285780", "jel": "#7A5C99", "anyag": "#4B5563", "energia": "#E07B39", "tevékenység": "#3E8E63"}
VASTAG = {"adat": 1.2, "jel": 1.2, "anyag": 2.6, "energia": 1.8, "tevékenység": 1.2}
STILUS = {"tevékenység": (0, (4, 2))}

def kontextusdiagram(df, rendszer, R=4.4, fajlnev=None):
    """Kontextusdiagram: az azonos irányú és típusú kölcsönhatások egy nyílra kerülnek."""
    entitasok = list(dict.fromkeys(df["entitas"]))
    n = len(entitasok)
    fig, ax = plt.subplots(figsize=(13, 10.5))
    ax.set_xlim(-R * 1.3 - 1.6, R * 1.3 + 1.6); ax.set_ylim(-R - 1.7, R + 1.0)
    ax.set_aspect("equal"); ax.axis("off")
    a, b = 2.0, 1.1                      # a rendszer-ellipszis féltengelyei
    w, h = 1.3, 0.42                     # az entitásdobozok fél szélessége és magassága
    ax.add_patch(Ellipse((0, 0), 2 * a, 2 * b, fc="#E6EEF6", ec="#285780", lw=2, zorder=3))
    ax.text(0, 0, rendszer, ha="center", va="center", fontsize=11, fontweight="bold", color="#1B3A57", zorder=4)
    for i, e in enumerate(entitasok):
        t = math.pi / 2 - 2 * math.pi * i / n
        ex, ey = R * 1.3 * math.cos(t), R * math.sin(t)
        ax.add_patch(FancyBboxPatch((ex - w, ey - h), 2 * w, 2 * h, boxstyle="round,pad=0.04",
                                    fc="#F1F2F4", ec="#6B7280", lw=1, zorder=3))
        ax.text(ex, ey, e, ha="center", va="center", fontsize=9, zorder=4)
        d = math.hypot(ex, ey); ux, uy = ex / d, ey / d          # egységvektor a rendszertől az entitás felé
        phi = math.atan2(ey, ex)
        r_e = 1 / math.sqrt((math.cos(phi) / a) ** 2 + (math.sin(phi) / b) ** 2)
        s_b = min(w / abs(ux) if ux else 1e9, h / abs(uy) if uy else 1e9) + 0.08
        csop = (df[df["entitas"] == e].groupby(["irany", "tipus"], sort=False)["kolcsonhatas"]
                .apply(lambda x: "\\n".join(x)).reset_index())
        k = len(csop)
        for j, c in csop.iterrows():
            eltol = (j - (k - 1) / 2) * 0.42
            nx, ny = -uy, ux
            p_rsz = ((r_e + 0.05) * ux + nx * eltol, (r_e + 0.05) * uy + ny * eltol)
            p_ent = (ex - s_b * ux + nx * eltol, ey - s_b * uy + ny * eltol)
            p1, p2 = (p_ent, p_rsz) if c["irany"] == "be" else (p_rsz, p_ent)
            ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=14,
                                         color=SZIN.get(c["tipus"], "black"), lw=VASTAG.get(c["tipus"], 1.2),
                                         linestyle=STILUS.get(c["tipus"], "-"), zorder=5))
            q = 0.35 + (0.3 * j / (k - 1) if k > 1 else 0.15)
            mx, my = (1 - q) * p_rsz[0] + q * p_ent[0], (1 - q) * p_rsz[1] + q * p_ent[1]
            ax.text(mx, my, c["kolcsonhatas"], fontsize=7.5, ha="center", va="center", zorder=6,
                    color=SZIN.get(c["tipus"], "black"),
                    bbox=dict(fc="white", ec=SZIN.get(c["tipus"], "black"), lw=0.4, pad=1.2, alpha=0.95))
    for i, (tip, sz) in enumerate(SZIN.items()):
        x0 = -R * 1.3 + i * 2.4
        ax.plot([x0, x0 + 0.7], [-R - 1.35] * 2, color=sz, lw=VASTAG[tip], linestyle=STILUS.get(tip, "-"))
        ax.text(x0 + 0.8, -R - 1.35, tip, va="center", fontsize=9)
    plt.tight_layout()
    if fajlnev:
        fig.savefig(fajlnev, bbox_inches="tight", dpi=150)
    plt.show()

kontextusdiagram(df, RENDSZER, fajlnev="kontextusdiagram.png")
'''),
    md("""
## Értelmezés

- A diagram **fekete doboz**: a rendszer belsejét szándékosan nem mutatja. Ha a középső alakzatba alrendszereket rajzolnál, az már architektúra, nem kontextus.
- A „csak bemenet” vagy „csak kimenet” jelzés nem feltétlenül hiba (az energiaszolgáltató felé valóban nem megy semmi), de mindig gondold végig, nem maradt-e ki egy visszairányú áramlás (visszaigazolás, rendelés, elszámolás).
- A kész interfészlista minden sora egy vagy több **interfészkövetelmény** forrása (Követelményírás eszközlap), a belső interfészeket pedig az N²-diagram tárja fel.
- A `kontextusdiagram.png` fájl a futtatás után letölthető (Colabban a bal oldali *Fájlok* panelről), és beilleszthető a projektdokumentációba.
"""),
]
