from _kozos import BETOLTO, code, fejresz, md

NEV = "funkciofa"
CIM = "Funkciófa és allokáció: hierarchia, szélesség, modularitás"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook egy funkciófából és egy allokációs táblázatból

1. kirajzolja a funkciófát, és szintenként ellenőrzi a lebontás szélességét (a 7 ± 2-es hüvelykujjszabály);
2. hőtérképként ábrázolja a funkciók és a forma elemei közötti allokációt;
3. kiszámítja a gazdátlan és a több gazdás (interfészt létrehozó) funkciókat, valamint az egy gazdás funkciók arányát mint egyszerű modularitási mutatót.

A beépített példa a KoboCella funkciófája és allokációja (kézikönyv 8. fejezet).
""", sablon="funkciofa_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Funkciófa és allokáció eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött funkciofa_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("funkciofa_sablon.xlsx")
    fa = pd.read_excel(fajl, sheet_name="Funkciófa", header=3, dtype=str).iloc[:, :3].dropna(subset=["Azonosító"])
    fa.columns = ["id", "funkcio", "szulo"]
    fa["szulo"] = fa["szulo"].fillna("")
    a = pd.read_excel(fajl, sheet_name="Allokáció", header=3, dtype=str)
    elemek = [c for c in a.columns[2:10] if not str(c).startswith("Unnamed")]
    a = a.dropna(subset=[a.columns[0], a.columns[1]])
    allok = pd.DataFrame({e: a[e].notna().astype(int).to_numpy() for e in elemek}, index=a.iloc[:, 0] + " " + a.iloc[:, 1])
else:
    fa = pd.DataFrame([
        ("0", "motor összeszerelése", ""), ("1", "alkatrészek előkészítése", "0"), ("1.1", "motorház befogása", "1"),
        ("1.2", "fedél pozicionálása", "1"), ("2", "csavarkötés létrehozása", "0"), ("2.1", "csavar adagolása", "2"),
        ("2.2", "csavar meghúzása", "2"), ("2.3", "nyomaték mérése", "2"), ("3", "minőség igazolása", "0"),
        ("3.1", "adatok naplózása", "3"), ("3.2", "hibás darab jelölése", "3"), ("3.3", "adatátadás a MES-nek", "3"),
        ("4", "ember védelme", "0"), ("4.1", "védőzóna figyelése", "4"), ("4.2", "mozgás korlátozása", "4"),
        ("4.3", "vészleállítás", "4"), ("5", "termék továbbítása", "0"), ("5.1", "kész motor kivétele", "5"),
        ("5.2", "elhelyezés a kiadóban", "5")], columns=["id", "funkcio", "szulo"])
    elemek = ["kobot, megfogó", "csavarozó egység", "asztal, adagolás", "biztonsági alrendszer", "cellavezérlés, HMI", "operátor"]
    hozzarendeles = {"1.1": [2, 5], "1.2": [0], "2.1": [2], "2.2": [0, 1], "2.3": [1], "3.1": [4], "3.2": [4, 5],
                     "3.3": [4], "4.1": [3], "4.2": [0, 3], "4.3": [3, 5], "5.1": [0], "5.2": [0]}
    nevek = dict(zip(fa["id"], fa["funkcio"]))
    allok = pd.DataFrame(0, index=[f"{k} {nevek[k]}" for k in hozzarendeles], columns=elemek)
    for i, (k, js) in enumerate(hozzarendeles.items()):
        allok.iloc[i, js] = 1
fa["szint"] = fa["id"].apply(lambda s: 0 if s == "0" else s.count(".") + 1)
fa["gyermekek"] = fa["id"].map(fa["szulo"].value_counts()).fillna(0).astype(int)
fa
'''),
    md("## A funkciófa és a szélesség ellenőrzése"),
    code('''
gyerek = {i: list(fa.loc[fa["szulo"] == i, "id"]) for i in fa["id"]}
nev = dict(zip(fa["id"], fa["funkcio"]))
gyoker = fa.loc[fa["szulo"] == "", "id"].iloc[0]

# levélalapú elrendezés: a levelek egyenletesen, a szülők a gyermekeik fölé
pozicio, szamlalo = {}, [0]
def elrendez(n, melyseg):
    if not gyerek[n]:
        pozicio[n] = (szamlalo[0], -melyseg); szamlalo[0] += 1
    else:
        for g in gyerek[n]:
            elrendez(g, melyseg + 1)
        xs = [pozicio[g][0] for g in gyerek[n]]
        pozicio[n] = (np.mean(xs), -melyseg)
elrendez(gyoker, 0)

fig, ax = plt.subplots(figsize=(max(9, szamlalo[0] * 0.95), 4.2))
for n, gs in gyerek.items():
    for g in gs:
        ax.plot([pozicio[n][0], pozicio[g][0]], [pozicio[n][1], pozicio[g][1]], color="#9FB7CF", lw=1)
for n, (x, y) in pozicio.items():
    ax.text(x, y, f"{n}\\n{nev[n]}", ha="center", va="center", fontsize=7.5, wrap=True,
            bbox=dict(boxstyle="round,pad=0.3", fc="#285780" if y == 0 else ("#E6EEF6" if gyerek[n] else "white"),
                      ec="#285780", lw=0.8), color="white" if y == 0 else "black")
ax.axis("off"); ax.set_title("Funkciófa")
plt.tight_layout(); plt.show()

szelesseg = fa[fa["gyermekek"] > 0][["id", "funkcio", "gyermekek"]].copy()
szelesseg["ellenőrzés"] = np.where(szelesseg["gyermekek"] > 9, "túl sok: közbülső szint?",
                          np.where(szelesseg["gyermekek"] == 1, "egy gyermek: felesleges szint?", "rendben"))
szelesseg
'''),
    md("## Allokáció és modularitás"),
    code('''
gazdak = allok.sum(axis=1)
osszegzes = pd.DataFrame({"gazdák száma": gazdak,
                          "állapot": np.where(gazdak == 0, "nincs gazdája!", np.where(gazdak == 1, "egy gazda", "interfész"))})
modularitas = (gazdak == 1).mean()
print(f"Gazdátlan funkciók: {(gazdak == 0).sum()} | interfészt létrehozó funkciók: {(gazdak > 1).sum()} | "
      f"egy gazdás funkciók aránya (modularitási mutató): {modularitas:.0%}")

fig, axs = plt.subplots(1, 2, figsize=(11, 5), gridspec_kw={"width_ratios": [3, 1]})
axs[0].imshow(allok.to_numpy(), cmap="Blues", vmin=0, vmax=1.4, aspect="auto")
axs[0].set_xticks(range(allok.shape[1]), allok.columns, rotation=35, ha="right", fontsize=8)
axs[0].set_yticks(range(allok.shape[0]), allok.index, fontsize=8)
for i in range(allok.shape[0]):
    for j in range(allok.shape[1]):
        if allok.iat[i, j]:
            axs[0].text(j, i, "×", ha="center", va="center", color="white", fontsize=10)
    if gazdak.iloc[i] > 1:
        axs[0].add_patch(plt.Rectangle((-0.5, i - 0.5), allok.shape[1], 1, fill=False, ec="#E07B39", lw=1.6))
axs[0].set_title("Allokáció (narancs keret: interfészt létrehozó funkció)", fontsize=10)
axs[1].barh(range(allok.shape[1]), allok.sum(axis=0), color="#4F7FAD")
axs[1].set_yticks(range(allok.shape[1]), allok.columns, fontsize=8); axs[1].invert_yaxis()
axs[1].set_title("Funkciók elemenként", fontsize=10)
plt.tight_layout(); plt.savefig("funkciofa_allokacio.png", bbox_inches="tight", dpi=150); plt.show()
osszegzes
'''),
    md("""
## Értelmezés

- **Gazdátlan funkció:** elveszett funkció; vagy hiányzik egy elem, vagy a funkció valójában nem kell.
- **Több gazdás funkció:** az elemek között interfész keletkezik, amelyet az N²-diagramon fel kell tüntetni és meg kell tervezni.
- **Sok funkciót ellátó elem** (a KoboCellánál a kobot): integrált elem; a módosítása több funkciót érint, ezért a regressziós tesztelés kiemelten fontos.
- A modularitási mutató csak durva jelzés. A modulok kialakításához az elemek közötti kapcsolatok elemzése (DSM, n2_dsm notebook) ad megbízhatóbb képet.
"""),
]
