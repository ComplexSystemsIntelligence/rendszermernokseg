from _kozos import BETOLTO, code, fejresz, md

NEV = "hta"
CIM = "Hierarchikus feladatelemzés (HTA): táblázatos HTA, időkeret és kezelő–gép idődiagram"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. a HTA-sablon soraiból felépíti a célhierarchiát, és táblázatos HTA-ként (Stanton formátumában) kiírja a terveket és a műveleteket;
2. összegzi a ciklusonként ismétlődő műveletek idejét, és összeveti a kezelő időkeretével;
3. kezelő–gép idődiagramot rajzol a ciklusidő-költségvetés gépi részeivel, a ciklusidő-követelménnyel és a ütemidővel;
4. összesíti az azonosított hibalehetőségeket típusonként.

A beépített példa a KoboCella kezelőjének feladatai (kézikönyv 11. fejezet; a ciklusidő-költségvetés a 6. fejezetben).
""", sablon="hta_sablon.xlsx", eszkozlap="Gyakorlati útmutató, HTA eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött hta_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
pd.set_option("display.max_colwidth", 60)
'''),
    md("## Adatok"),
    code('''
OSZLOPOK = ["id", "nev", "szulo", "terv", "ido", "gyak", "ciklus", "szint", "ido_ciklus", "hibatipus", "hiba", "kovetkezmeny", "javaslat"]
if SAJAT_SABLON:
    fajl = sablon_betoltese("hta_sablon.xlsx")
    nyers = pd.read_excel(fajl, sheet_name="HTA", header=None)
    idokeret = float(nyers.iloc[2, 3])
    hta = nyers.iloc[5:, :13].copy()
    hta.columns = OSZLOPOK
    hta = hta[hta["id"].notna() & hta["nev"].notna()]
    hta = hta[~hta["id"].astype(str).str.startswith(("A kezelő", "Tartalék", "Műveletek", "Azonosított", "Ebből"))]
else:
    idokeret = 18.0
    sorok = [
        ("0", "motorok szerelése a KoboCellában egy műszakon át", "", "1, majd 2 ismételve; ha hibajelzés: 3, utána vissza 2-re; a műszak végén 4", None, None, "", "", "", "", ""),
        ("1", "műszak indítása", "0", "1.1 > 1.2 > 1.3", None, None, "", "", "", "", ""),
        ("1.1", "bejelentkezés a HMI-n", "1", "", 30, None, "nem", "", "", "", ""),
        ("1.2", "típusprogram ellenőrzése", "1", "", 20, None, "nem", "tévedés", "rossz típusprogram marad betöltve", "hibás nyomaték egy teljes sorozaton", "a HMI a gyártási rendelés alapján javasolja a programot"),
        ("1.3", "csavarellátás ellenőrzése", "1", "", 40, None, "nem", "kihagyás", "az ellenőrzés elmarad", "leállás a műszak elején", "töltöttségérzékelő az adagolóban"),
        ("2", "egy motor szerelése (ciklus)", "0", "2.1 > 2.2 > 2.3 > 2.4 > 2.5", None, None, "", "", "", "", ""),
        ("2.1", "motorház kivétele a tálcáról", "2", "", 4, 1, "igen", "", "", "", ""),
        ("2.2", "motorház behelyezése a befogóba", "2", "", 6, 1, "igen", "megcsúszás", "nem ül fel teljesen a befogóra", "a kobot nem indul, időveszteség", "befogóérzékelő, HMI-visszajelzés"),
        ("2.3", "fedél ráhelyezése", "2", "", 5, 1, "igen", "megcsúszás", "fordítva helyezi fel a fedelet", "tömítetlen motor", "aszimmetrikus illesztőcsapok (poka-yoke)"),
        ("2.4", "kilépés a zónából", "2", "", 1.5, 1, "igen", "szabályszegés", "a zónában marad, hogy gyorsabb legyen", "a kobot csökkentett sebességgel dolgozik", "a lézerszkenner csak zónaelhagyás után engedi a teljes sebességet"),
        ("2.5", "indítás nyugtázása", "2", "", 1.5, 1, "igen", "", "", "", ""),
        ("3", "hibajelzés kezelése", "0", "3.1 > 3.2 > 3.3", None, None, "", "", "", "", ""),
        ("3.1", "hibakód leolvasása", "3", "", 5, None, "nem", "tévedés", "félreérti a hibakódot", "jó darab a selejtbe vagy fordítva", "a HMI a hiba helyét is mutatja"),
        ("3.2", "hibás darab a selejtdobozba", "3", "", 8, None, "nem", "kihagyás", "a hibás darab a kiadóba kerül", "hibás motor a vevőnél", "a kiadó csak a selejtdoboz érzékelőjének jelzése után enged"),
        ("3.3", "nyugtázás", "3", "", 2, None, "nem", "", "", "", ""),
        ("4", "műszak zárása", "0", "4.1 > 4.2", None, None, "", "", "", "", ""),
        ("4.1", "adatok lezárása, műszakátadás", "4", "", 60, None, "nem", "kihagyás", "nyitott eltérés nem kerül át", "a következő műszak nem tud a hibáról", "strukturált átadólap a HMI-n"),
        ("4.2", "terület rendbetétele", "4", "", 300, None, "nem", "", "", "", ""),
    ]
    hta = pd.DataFrame([(a, b, c, d, e, f, g, None, None, h, i, j, k) for a, b, c, d, e, f, g, h, i, j, k in sorok], columns=OSZLOPOK)

hta["id"] = hta["id"].astype(str).str.strip()
hta["szulo"] = hta["szulo"].fillna("").astype(str).str.strip()
hta["szint"] = hta["id"].apply(lambda s: 0 if s == "0" else s.count(".") + 1)
for c in ("terv", "ciklus", "hibatipus", "hiba", "kovetkezmeny", "javaslat"):
    hta[c] = hta[c].fillna("").astype(str)
hta["ido"] = pd.to_numeric(hta["ido"], errors="coerce")
hta["gyak"] = pd.to_numeric(hta["gyak"], errors="coerce")
gyermek = {i: list(hta.loc[hta["szulo"] == i, "id"]) for i in hta["id"]}
print(f"{len(hta)} elem, {sum(1 for v in gyermek.values() if not v)} legalsó szintű művelet, mélység: {hta['szint'].max()}")

# gépi összetevők a ciklusidő-költségvetésből (kézikönyv 6. fejezet)
GEP = [("kobot: fedél pozicionálása és rögzítése", 9.0), ("csavarozó egység: 8 csavar (8 × 3,2 s)", 25.6), ("kobot: kész motor kivétele", 6.0)]
KOVETELMENY, UTEMIDO = 75.0, 88.7   # R-01 és az ütemidő [s]
'''),
    md("## Táblázatos HTA"),
    code('''
def behuzas(i):
    return "    " * hta.loc[hta["id"] == i, "szint"].iloc[0]

print("TÁBLÁZATOS HTA")
for _, s in hta.iterrows():
    jel = "" if gyermek[s["id"]] else "  •"
    ido = f"  [{s['ido']:g} s]" if pd.notna(s["ido"]) else ""
    print(f"{behuzas(s['id'])}{s['id']} {s['nev']}{ido}{jel}")
    if gyermek[s["id"]]:
        print(f"{behuzas(s['id'])}    terv: {s['terv'] or 'HIÁNYZIK!'}")

hianyzo_terv = [i for i, gy in gyermek.items() if gy and not hta.loc[hta["id"] == i, "terv"].iloc[0]]
if hianyzo_terv:
    print("\\nFIGYELEM: ezekhez a részcélokhoz nincs terv:", hianyzo_terv)
'''),
    md("## Időkeret és kezelő–gép idődiagram"),
    code('''
ciklus = hta[(hta["ciklus"] == "igen") & hta["ido"].notna()].copy()
ciklus["gyak"] = ciklus["gyak"].fillna(1)
ciklus["ido_ciklus"] = ciklus["ido"] * ciklus["gyak"]
kezelo = ciklus["ido_ciklus"].sum()
print(f"A kezelő ideje ciklusonként: {kezelo:.1f} s, időkeret: {idokeret:.1f} s, tartalék: {idokeret - kezelo:+.1f} s")
gepi = sum(t for _, t in GEP)
soros = kezelo + gepi
print(f"Soros ciklusidő (kezelő + gép): {soros:.1f} s; követelmény: {KOVETELMENY:.0f} s; tartalék: {KOVETELMENY - soros:.1f} s ({(KOVETELMENY - soros) / KOVETELMENY:.0%})")
print(f"A kezelő lekötöttsége a soros ciklusban: {kezelo / soros:.0%}")

fig, ax = plt.subplots(figsize=(12, 3.6))
t = 0
szinek = ["#285780", "#4A7AA8", "#7FA6CC", "#B8CEE4", "#DCE7F2"]
for k, (_, s) in enumerate(ciklus.iterrows()):
    ax.barh(1, s["ido_ciklus"], left=t, color=szinek[k % 5], edgecolor="white")
    ax.text(t + s["ido_ciklus"] / 2, 1.42 if (k % 2 == 0 or s["ido_ciklus"] >= 3) else 1.56, s["id"], ha="center", fontsize=8)
    t += s["ido_ciklus"]
gszin = ["#E07B39", "#3E8E63", "#E07B39"]
for k, (n, d) in enumerate(GEP):
    ax.barh(0, d, left=t, color=gszin[k], edgecolor="white")
    ax.text(t + d / 2, 0, n.split(":")[0], ha="center", va="center", fontsize=8, color="white")
    if k == 1:
        ax.barh(1, d, left=t, color="none", edgecolor="#999999", hatch="//", lw=0.8)
        ax.text(t + d / 2, 1, "párhuzamos: szemrevételezés,\\nkövetkező darab előkészítése", ha="center", va="center", fontsize=7.5)
    t += d
ax.axvline(KOVETELMENY, color="#B83A3A", ls="--"); ax.text(KOVETELMENY + 0.5, 1.45, "R-01: 75 s", color="#B83A3A", fontsize=8)
ax.axvline(UTEMIDO, color="#666666", ls=":"); ax.text(UTEMIDO + 0.5, 1.45, f"ütemidő: {UTEMIDO:g} s", color="#666666", fontsize=8)
ax.set_yticks([0, 1]); ax.set_yticklabels(["gép", "kezelő"]); ax.set_ylim(-0.6, 1.75)
ax.set_xlim(0, UTEMIDO + 14); ax.set_xlabel("idő a ciklus kezdetétől [s]"); ax.grid(axis="x", alpha=0.3)
ax.set_title(f"Kezelő–gép idődiagram: soros ciklusidő {soros:.1f} s, tartalék {KOVETELMENY - soros:.1f} s", fontsize=10)
plt.tight_layout(); plt.savefig("hta_idodiagram.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("## Hibalehetőségek"),
    code('''
hibak = hta[hta["hibatipus"] != ""][["id", "nev", "hibatipus", "hiba", "kovetkezmeny", "javaslat"]]
print(hibak["hibatipus"].value_counts().to_string())
hibak
'''),
    md("""
## Értelmezés

- A ciklusonként ismétlődő öt művelet összesen 18 s, pontosan a kezelő időkerete: a kezelői részben nincs tartalék, a cella tartaléka (16,4 s) a gépi részekből és a követelményből adódik. Ha a kezelői időbecslések a próbaüzemben nőnek, ezt a tartalékot fogyasztják.
- A kezelő a soros ciklusnak csak mintegy harmadában van lekötve. A csavarozás alatti szabad idő a szemrevételezésre és a következő darab előkészítésére jut; a kézikönyv 12. fejezete szerint a csapat ide tette a minőségi ellenőrzést is, hogy a kezelő ne csak „adogató” legyen.
- A hibalehetőségek közül a 2.2 és a 2.3 (megcsúszás) és a 2.4 (szabályszegés) a ciklus része, tehát minden ciklusban előfordulhat: ezekre műszaki megoldás (érzékelő, poka-yoke, biztonsági reteszelés) kell, nem csak oktatás. A ritka 3-as részcélnál a tévedés és a kihagyás a jellemző: itt a HMI lépésenkénti vezetése segít.
- A hibalehetőségek számszerű értékelését (HEART) és a megelőzés módjait a kézikönyv 13. fejezete tárgyalja.
"""),
]
