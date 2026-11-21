from _kozos import BETOLTO, code, fejresz, md

NEV = "kovetelmeny_ellenorzes"
CIM = "Követelmények automatikus megfogalmazás-ellenőrzése"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook szabályalapú ellenőrzést végez magyar nyelvű követelményszövegeken. A szabályok az INCOSE
követelményírási útmutatóján és az ISO/IEC/IEEE 29148 szabványon alapulnak (egy „kell” mondatonként,
kétértelmű kifejezések kerülése, TBD helyett TBR, mérhetőség, a rendszer mint alany), és a kézikönyv
6. fejezetében tárgyalt ismérveket követik.

Az ellenőrzés csak a *megfogalmazást* vizsgálja. Azt, hogy egy követelmény *helyes*-e, vagyis a valódi igényt
fejezi-e ki, csak az érdekelt felekkel közösen lehet eldönteni.
""", sablon="kovetelmeny_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Követelményírás eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött kovetelmeny_sablon.xlsx „Nyilvántartás” lapjának ellenőrzése
''' + BETOLTO + '''
import re
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## A követelmények betöltése"),
    code('''
PELDA = [
    ("R-01", "A cellának egy motort legfeljebb 75 s alatt kell összeszerelnie."),
    ("R-03", "A cellának a nyolc csavart 4,0 ± 0,2 Nm nyomatékkal kell meghúznia."),
    ("R-05", "A munkaasztalon végzett minden műveletnek legfeljebb 20°-os törzshajlítással elvégezhetőnek kell lennie."),
    ("R-07", "Ha egy csavar nyomatéka a tűrésen kívül esik, akkor a cellának a motort hibásként kell megjelölnie."),
    ("R-11", "Amíg személy tartózkodik a védőzónában, a kobot sebességének legfeljebb 250 mm/s-nak kell lennie."),
    ("R-30", "A cellának gyorsnak és felhasználóbarátnak kell lennie."),
    ("R-31", "A cellának meg kell jelenítenie a hibákat és naplóznia kell az eseményeket, stb."),
    ("R-32", "Az operátor ellenőrzi a kész motort."),
    ("R-33", "A csavarozó egység pontossága TBD."),
    ("R-34", "A rendszernek lehetőleg minimalizálnia kell a selejtet és/vagy az utómunkát."),
    ("R-35", "A kijelzőt a hibákról az operátornak tájékoztatnia kell."),
]
if SAJAT_SABLON:
    fajl = sablon_betoltese("kovetelmeny_sablon.xlsx")
    kov = pd.read_excel(fajl, sheet_name="Nyilvántartás", header=3)[["Azonosító", "Követelmény szövege"]]
    kov = kov.dropna().rename(columns={"Azonosító": "id", "Követelmény szövege": "szoveg"})
else:
    kov = pd.DataFrame(PELDA, columns=["id", "szoveg"])
print(len(kov), "követelmény")
'''),
    md("## A szabályok"),
    code('''
KETERTELMU = ["megfelelő", "gyors", "rugalmas", "felhasználóbarát", "könnyen", "könnyű", "lehetőleg", "optimális",
              "maximalizál", "minimalizál", "kellően", "általában", "szükség szerint", "stb.", "és/vagy",
              "többek között", "ésszerű", "hatékony", "megbízható", "biztonságos", "modern", "korszerű"]
NEM_RENDSZER_ALANY = re.compile(r"^(az|a) (operátor|felhasználó|karbantartó|kezelő|ügyintéző)", re.I)
SZAM = re.compile(r"\\d")

def ellenoriz(szoveg):
    s = szoveg.strip()
    kicsi = s.lower()
    hibak = []
    n_kell = len(re.findall(r"\\bkell\\b", kicsi))
    if n_kell == 0:
        hibak.append("nincs „kell”: cél vagy tény?")
    if n_kell > 1:
        hibak.append("több „kell”: bontsd szét (egyediség)")
    talalt = [k for k in KETERTELMU if k in kicsi]
    if talalt:
        hibak.append("kétértelmű kifejezés: " + ", ".join(talalt))
    if "tbd" in kicsi:
        hibak.append("TBD: adj legjobb becslést TBR jelöléssel")
    if not SZAM.search(s):
        hibak.append("nincs számérték: mérhető, verifikálható?")
    if NEM_RENDSZER_ALANY.search(s):
        hibak.append("az alany nem a rendszer: működési leírás?")
    if re.search(r"\\b(és|vagy)\\b", kicsi) and n_kell >= 1 and len(s) > 90:
        hibak.append("hosszú, összetett mondat: egyetlen állítás?")
    return hibak

kov["hibák"] = kov["szoveg"].apply(ellenoriz)
kov["hibák száma"] = kov["hibák"].str.len()
pd.set_option("display.max_colwidth", 120)
kov[["id", "szoveg", "hibák"]]
'''),
    md("## Összesítés"),
    code('''
osszes = kov.explode("hibák").dropna(subset=["hibák"])
osszes["szabály"] = osszes["hibák"].str.split(":").str[0]
gyak = osszes["szabály"].value_counts()
print(f"Hibátlan: {(kov['hibák száma'] == 0).sum()} / {len(kov)}")
fig, ax = plt.subplots(figsize=(7, 3.5))
gyak.sort_values().plot.barh(ax=ax, color="#285780")
ax.set_xlabel("előfordulás"); ax.set_title("A jelzett hibák típusai")
plt.tight_layout(); plt.show()
'''),
    md("""
## Értelmezés

- A jelzés **figyelmeztetés**, nem ítélet. Egy funkcionális követelményben (például „a cellának a motort hibásként kell megjelölnie”) nem feltétlenül kell számnak lennie; ilyenkor a teljesítménykövetelmény egy külön sorban szerepel.
- A „kétértelmű kifejezés” listája bővíthető. Projektenként érdemes a gyakori hibákat felvenni.
- Nagy nyelvi modellel a jelzett követelményekre javítási javaslat is kérhető (lásd a Követelményírás eszközlap mintapromptjait). A javasolt szöveget mindig vesd össze a forrásával és az indoklással.
"""),
]
