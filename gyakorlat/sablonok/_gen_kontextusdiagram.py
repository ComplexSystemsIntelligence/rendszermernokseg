"""Kontextusdiagram és interfészlista sablon."""
from _kozos import *  # noqa: F401,F403

TIPUSOK = ["adat", "jel", "anyag", "energia", "tevékenység"]
IRANY = ["be", "ki"]
ELEM = ["összekötő", "szigetelő", "átalakító", "–"]

PELDA_IF = [
    ("Felhasználók", "kölcsönzési kérés (alkalmazás vagy kártya)", "be", "adat", "átalakító", "napi 600–900", "alkalmazásfejlesztő"),
    ("Felhasználók", "kölcsönzési visszaigazolás, díjtájékoztatás", "ki", "adat", "átalakító", "kölcsönzésenként", "alkalmazásfejlesztő"),
    ("Felhasználók", "feltöltött elektromos kerékpár", "ki", "anyag", "összekötő", "kölcsönzésenként", "üzemeltetési vezető"),
    ("Felhasználók", "visszahozott kerékpár", "be", "anyag", "összekötő", "kölcsönzésenként", "üzemeltetési vezető"),
    ("Felhasználók", "hibabejelentés", "be", "adat", "átalakító", "heti 20–40", "ügyfélszolgálat"),
    ("Fizetési szolgáltató", "fizetési kérelem", "ki", "adat", "összekötő", "kölcsönzésenként", "pénzügy"),
    ("Fizetési szolgáltató", "fizetési visszaigazolás", "be", "adat", "összekötő", "kölcsönzésenként", "pénzügy"),
    ("Helyi közlekedési társaság", "érvényes bérletek listája", "be", "adat", "összekötő", "naponta", "informatika"),
    ("Helyi közlekedési társaság", "közös bérletes kölcsönzések elszámolása", "ki", "adat", "összekötő", "havonta", "pénzügy"),
    ("Önkormányzat", "közterület-használati engedély", "be", "adat", "–", "állomásonként, egyszer", "projektvezető"),
    ("Önkormányzat", "használati és kibocsátási jelentés", "ki", "adat", "–", "havonta", "üzemeltetési vezető"),
    ("Energiaszolgáltató", "villamos energia a dokkolóknak", "be", "energia", "átalakító", "folyamatos", "üzemeltetési vezető"),
    ("Navigációs szolgáltatók", "állomások helye és szabad kerékpárok száma", "ki", "adat", "összekötő", "percenként", "informatika"),
    ("Rendőrség", "lopás- és rongálásbejelentés", "ki", "adat", "–", "esetenként", "üzemeltetési vezető"),
    ("Kerékpár-beszállító", "pótalkatrész-rendelés, garanciális igény", "ki", "adat", "–", "havonta", "szervizvezető"),
    ("Kerékpár-beszállító", "pótalkatrész, garanciális javítás", "be", "anyag", "–", "havonta", "szervizvezető"),
    ("Akkumulátor-újrahasznosító", "elhasznált akkumulátorok", "ki", "anyag", "–", "negyedévente", "szervizvezető"),
]

FEJ = ["Azonosító", "Külső entitás", "Kölcsönhatás (mi megy át a határon?)", "Irány (be/ki)", "Típus",
       "Interfészelem", "Gyakoriság, mennyiség", "Felelős (gazda)", "Kapcsolódó követelmény", "Ellenőrzés"]
SZEL = [11, 26, 44, 10, 13, 14, 20, 20, 18, 30]


def ellenorzes(r):
    return (f'=IF(B{r}="","",IF(OR(D{r}="",E{r}=""),"Hiányzó irány vagy típus",'
            f'IF(OR(LOWER(TRIM(C{r}))="adat",LOWER(TRIM(C{r}))="adatok",LOWER(TRIM(C{r}))="információ",'
            f'LOWER(TRIM(C{r}))="kommunikáció",LOWER(TRIM(C{r}))="adatcsere"),"Túl általános címke",'
            f'IF(H{r}="","Nincs gazdája","rendben"))))')


def interfesz_lap(wb, nev, adatok, ures):
    ws = wb.create_sheet(nev)
    cimsor(ws, "Interfészlista (a kontextusdiagram táblázatos alakja)",
           "Egy sor = egy kölcsönhatás egy irányban. Kétirányú kapcsolatot két sorban rögzíts.")
    sorok = [[f"IF-{i:02d}", *a] for i, a in enumerate(adatok, start=1)]
    utolso = tablazat(ws, 4, FEJ, SZEL, sorok, bemeneti_oszlopok=range(1, 10),
                      kepletek={10: ellenorzes}, uressor=ures)
    legordulo(ws, f"D5:D{utolso}", IRANY, "Irány")
    legordulo(ws, f"E5:E{utolso}", TIPUSOK, "Típus")
    legordulo(ws, f"F5:F{utolso}", ELEM, "Interfészelem")
    megjegyzes(ws["C4"], "Konkrét címkét írj: mi megy át a határon? Kerüld az „adat”, „kommunikáció” jellegű címkéket.")
    megjegyzes(ws["F4"], "Kossiakoff és mtsai (2011): összekötő (átvisz), szigetelő (gátol), átalakító (a közeg formáját változtatja).")
    ws.freeze_panes = "C5"
    return ws, utolso


def entitas_lap(wb, nev, iflap, entitasok, ures, utolso_if):
    ws = wb.create_sheet(nev)
    cimsor(ws, "Külső entitások és ellenőrzés",
           "Írd be a külső entitásokat; a darabszámok és az ellenőrzés az interfészlistából számolódik.")
    fej = ["Külső entitás", "Bemenetek száma", "Kimenetek száma"] + [f"{t}" for t in TIPUSOK] + ["Ellenőrzés"]
    fejlec(ws, 4, fej, [28, 12, 12, 9, 9, 9, 9, 12, 32])
    rng = lambda col: f"'{iflap}'!${col}$5:${col}${utolso_if}"
    r = 4
    for e in list(entitasok) + [None] * ures:
        r += 1
        bemenet(ws.cell(row=r, column=1), e)
        keplet(ws.cell(row=r, column=2), f'=IF(A{r}="","",COUNTIFS({rng("B")},A{r},{rng("D")},"be"))')
        keplet(ws.cell(row=r, column=3), f'=IF(A{r}="","",COUNTIFS({rng("B")},A{r},{rng("D")},"ki"))')
        for j, t in enumerate(TIPUSOK, start=4):
            keplet(ws.cell(row=r, column=j), f'=IF($A{r}="","",COUNTIFS({rng("B")},$A{r},{rng("E")},"{t}"))')
        keplet(ws.cell(row=r, column=9),
               f'=IF(A{r}="","",IF(B{r}+C{r}=0,"Nincs kölcsönhatás – kell-e?",'
               f'IF(B{r}=0,"Csak kimenet – rendben?",IF(C{r}=0,"Csak bemenet – rendben?","rendben"))))')
    r += 2
    szoveg(ws.cell(row=r, column=1), "Összesen", felkov=True)
    for j in range(2, 9):
        col = get_column_letter(j)
        keplet(ws.cell(row=r, column=j), f"=SUM({col}5:{col}{r - 2})", felkov=True)
    ws.freeze_panes = "B5"
    return ws


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Kontextusdiagram és interfészlista – sablon", [
        "■ Mire való? A rendszer határának kijelölése: mely külső entitásokkal és milyen áramlásokkal áll kapcsolatban a rendszer.",
        "1. Az „Interfészlista” lapon minden sor egy kölcsönhatás egy irányban: melyik külső entitással, mi megy át a határon, milyen irányba és milyen típusú (adat, jel, anyag, energia, tevékenység).",
        "2. A címke legyen konkrét (például „fizetési kérelem”), ne általános („adatcsere”). Az „Ellenőrzés” oszlop figyelmeztet a hiányokra és a túl általános címkékre.",
        "3. Az „Entitások” lapon sorold fel a külső entitásokat pontosan ugyanazzal a névvel, mint az interfészlistában. A lap megszámolja a bemeneteket, a kimeneteket és a típusokat, és jelzi a gyanús eseteket.",
        "4. A diagramot rajzold meg kézzel vagy diagramszerkesztővel, vagy futtasd a kontextusdiagram.ipynb notebookot, amely ebből a táblázatból automatikusan felrajzolja.",
        "■ Példa: a „Példa –” kezdetű lapok a VárosiBringa kitöltött interfészlistáját és entitáslistáját mutatják.",
    ])
    interfesz_lap(wb, "Interfészlista", [], 40)
    entitas_lap(wb, "Entitások", "Interfészlista", [], 15, 44)
    _, u = interfesz_lap(wb, "Példa – interfészek", PELDA_IF, 5)
    ent = list(dict.fromkeys(a[0] for a in PELDA_IF))
    entitas_lap(wb, "Példa – entitások", "Példa – interfészek", ent, 2, u)
    return mentes(wb, "kontextusdiagram_sablon.xlsx")


if __name__ == "__main__":
    keszit()
