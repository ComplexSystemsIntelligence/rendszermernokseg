from _kozos import BETOLTO, code, fejresz, md

NEV = "funkciomegosztas"
CIM = "Funkciómegosztás és automatizálási profil: Fitts-szempontok, LOA-hőtérkép, átvételi kockázatok"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. a funkciómegosztási sablonból összesíti, hány szempontból jobb a gép, illetve az ember, és jelzi a döntés és a jelölések ellentmondásait;
2. hőtérképen mutatja az automatizálási szinteket (Sheridan–Verplank, 1–10) a négy információfeldolgozási szakaszban (Parasuraman–Sheridan–Wickens);
3. kigyűjti azokat a funkciókat, amelyeket normál üzemben a gép végez, de leromlott üzemben az embernek kell átvennie, és megjelöli, ahol a magas döntési automatizálás miatt a készségek leépülésével kell számolni.

A beépített példa a KoboCella tizenhárom részfunkciója (kézikönyv 12. fejezet).
""", sablon="funkciomegosztas_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Funkciómegosztás eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött funkciomegosztas_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
SZAKASZOK = ["információgyűjtés", "elemzés", "döntés", "végrehajtás"]
'''),
    md("## Adatok"),
    code('''
OSZL = ["id", "funkcio", "sebesseg", "kovetkezetesseg", "itelet", "varatlan", "koltseg", "gep_db", "ember_db", "eset", "dontes",
        "jelzes", "loa1", "loa2", "loa3", "loa4", "loa_atlag", "leromlott", "atvetel", "indoklas"]
if SAJAT_SABLON:
    fajl = sablon_betoltese("funkciomegosztas_sablon.xlsx")
    df = pd.read_excel(fajl, sheet_name="Megosztás", header=3).iloc[:, :20]
    df.columns = OSZL
    df = df[df["id"].notna() & df["funkcio"].notna()]
else:
    sorok = [
        ("1.1", "motorház befogása", "G", "G", "E", "E", "E", 2, "ember", (3, 1, 1, 1), "ember"),
        ("1.2", "fedél pozicionálása", "G", "G", "=", "E", "=", 3, "gép", (8, 7, 7, 8), "ember"),
        ("2.1", "csavar adagolása", "G", "G", "=", "=", "G", 5, "gép", (9, 8, 8, 9), "gép"),
        ("2.2", "csavar meghúzása", "G", "G", "=", "E", "G", 3, "gép", (9, 7, 7, 8), "ember"),
        ("2.3", "nyomaték mérése", "G", "G", "=", "=", "G", 5, "gép", (10, 9, 8, 9), "gép"),
        ("3.1", "adatok naplózása", "G", "G", "=", "=", "G", 5, "gép", (10, 10, 9, 10), "gép"),
        ("3.2", "hibás darab jelölése", "G", "G", "E", "E", "=", 1, "megosztott", (9, 8, 4, 2), "ember"),
        ("3.3", "adatátadás a MES-nek", "G", "G", "=", "=", "G", 5, "gép", (10, 10, 10, 10), "gép"),
        ("4.1", "védőzóna figyelése", "G", "G", "=", "=", "=", 5, "gép", (10, 9, 10, 10), "gép"),
        ("4.2", "mozgás korlátozása", "G", "G", "=", "=", "=", 5, "gép", (10, 9, 10, 10), "gép"),
        ("4.3", "vészleállítás", "G", "=", "E", "E", "=", 1, "megosztott", (9, 8, 7, 10), "ember"),
        ("5.1", "kész motor kivétele", "G", "G", "=", "=", "=", 3, "gép", (8, 7, 7, 8), "ember"),
        ("5.2", "elhelyezés a kiadóban", "G", "G", "=", "=", "=", 3, "gép", (8, 7, 7, 8), "ember"),
    ]
    df = pd.DataFrame([dict(zip(["id", "funkcio", "sebesseg", "kovetkezetesseg", "itelet", "varatlan", "koltseg", "eset", "dontes"], s[:9]),
                            loa1=s[9][0], loa2=s[9][1], loa3=s[9][2], loa4=s[9][3], leromlott=s[10]) for s in sorok])
SZEMP = ["sebesseg", "kovetkezetesseg", "itelet", "varatlan", "koltseg"]
df["gep_db"] = (df[SZEMP] == "G").sum(axis=1)
df["ember_db"] = (df[SZEMP] == "E").sum(axis=1)
LOA = ["loa1", "loa2", "loa3", "loa4"]
df[LOA] = df[LOA].apply(pd.to_numeric, errors="coerce")
df["cimke"] = df["id"].astype(str) + " " + df["funkcio"]
print(df["dontes"].value_counts().to_string())
'''),
    md("## Ellentmondások a jelölések és a döntés között"),
    code('''
def jelzes(s):
    if s["dontes"] == "gép" and s["ember_db"] > s["gep_db"]:
        return "az ember több szempontból jobb, mégis gépi"
    if s["dontes"] == "ember" and s["gep_db"] > s["ember_db"] + 1:
        return "a gép több szempontból jobb, mégis emberi: az indoklás (költség, elfogadás) legyen írásban"
    if s["eset"] == 6:
        return "egyik sem elfogadható: újratervezés"
    return ""
df["jelzes"] = df.apply(jelzes, axis=1)
ell = df.loc[df["jelzes"] != "", ["cimke", "gep_db", "ember_db", "dontes", "jelzes"]]
print(ell.to_string(index=False) if len(ell) else "Nincs ellentmondás a szempontonkénti jelölések és a döntések között.")
'''),
    md("## Automatizálási profil"),
    code('''
M = df[LOA].to_numpy(float)
fig, axs = plt.subplots(1, 2, figsize=(12, 0.42 * len(df) + 1.6), gridspec_kw={"width_ratios": [3, 2]})
im = axs[0].imshow(M, cmap="Blues", vmin=1, vmax=10, aspect="auto")
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        axs[0].text(j, i, f"{M[i, j]:.0f}", ha="center", va="center", fontsize=8, color="white" if M[i, j] >= 6 else "black")
axs[0].set_xticks(range(4)); axs[0].set_xticklabels(SZAKASZOK, fontsize=8)
axs[0].set_yticks(range(len(df))); axs[0].set_yticklabels([f"{c}  [{d}]" for c, d in zip(df["cimke"], df["dontes"])], fontsize=8)
axs[0].set_title("Automatizálási szint (1 kézi – 10 teljesen automatikus)", fontsize=10)
plt.colorbar(im, ax=axs[0], fraction=0.03)
atl = M.mean(axis=0)
axs[1].plot(range(4), atl, "o-", color="#285780", lw=2, label="átlag")
axs[1].fill_between(range(4), M.min(axis=0), M.max(axis=0), color="#B8CEE4", alpha=0.5, label="tartomány")
for j, v in enumerate(atl):
    axs[1].text(j, v + 0.35, f"{v:.1f}", ha="center", fontsize=8)
axs[1].set_xticks(range(4)); axs[1].set_xticklabels(SZAKASZOK, fontsize=8); axs[1].set_ylim(0, 11)
axs[1].set_ylabel("automatizálási szint"); axs[1].grid(alpha=0.3); axs[1].legend(fontsize=8, loc="lower left")
axs[1].set_title("A rendszer automatizálási profilja", fontsize=10)
plt.tight_layout(); plt.savefig("loa_hoterkep.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("## Átvétel leromlott üzemben"),
    code('''
atvetel = df[(df["dontes"] != "ember") & (df["leromlott"] == "ember")].copy()
atvetel["kockazat"] = np.where(atvetel["loa3"] >= 7, "készségvesztés: rendszeres kézi gyakorlás kell",
                               "átvétel: eljárásleírás és HMI-támogatás kell")
print(f"{len(atvetel)} funkciót kell az embernek átvennie leromlott üzemben.")
atvetel[["cimke", "dontes", "loa3", "loa4", "kockazat"]]
'''),
    md("""
## Értelmezés

- A KoboCella tizenhárom funkciójából tíz gépi, kettő megosztott és egy emberi. Az egyetlen emberi funkció (a motorház befogása) az, ahol az ítélőképesség, a váratlan helyzetek és a költség az ember mellett szól.
- A profil az információgyűjtésben a legmagasabb, a döntésben a legalacsonyabb. A két megosztott funkció (a hibás darab jelölése és a vészleállítás) döntési szintje 4, illetve 7: a gép jelez, de a következményekről az ember dönt, vagy a döntést a gép is meghozhatja, az ember pedig mindig beavatkozhat.
- Hat funkciót leromlott üzemben (UM-7) az embernek kell átvennie. Ahol a döntési szint normál üzemben 7 vagy magasabb, ott Bainbridge „automatizálási iróniája” fenyeget: a kezelő éppen azt nem gyakorolja, amire a legnagyobb szükség lenne. Ezért írta elő a csapat a negyedéves kézi gyakorlást (kézikönyv 12. fejezet).
"""),
]
