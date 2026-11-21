"""Funkciófa és allokációs táblázat (eszközlap: Funkciófa és allokáció)."""
from _kozos import *  # noqa: F401,F403

FA = [  # ID, funkció, szülő
    ("0", "motor összeszerelése", ""),
    ("1", "alkatrészek előkészítése", "0"),
    ("1.1", "motorház befogása", "1"),
    ("1.2", "fedél pozicionálása", "1"),
    ("2", "csavarkötés létrehozása", "0"),
    ("2.1", "csavar adagolása", "2"),
    ("2.2", "csavar meghúzása", "2"),
    ("2.3", "nyomaték mérése", "2"),
    ("3", "minőség igazolása", "0"),
    ("3.1", "adatok naplózása", "3"),
    ("3.2", "hibás darab jelölése", "3"),
    ("3.3", "adatátadás a MES-nek", "3"),
    ("4", "ember védelme", "0"),
    ("4.1", "védőzóna figyelése", "4"),
    ("4.2", "mozgás korlátozása", "4"),
    ("4.3", "vészleállítás", "4"),
    ("5", "termék továbbítása", "0"),
    ("5.1", "kész motor kivétele", "5"),
    ("5.2", "elhelyezés a kiadóban", "5"),
]
SZOTAR = ["robot", "kobot", "szoftver", "alkalmazás", "applikáció", "PLC", "kamera", "szenzor", "lézer", "szkenner",
          "RFID", "QR-kód", "futószalag", "szállítószalag", "Excel", "adatbázis", "okostelefon", "mobiltelefon", "e-mail"]
KEPZOK = ["ás ", "és ", "ása ", "ése ", "ását ", "ését ", "zás ", "zés ", "tele ", "telé ", "elme ", "lása ", "lése "]
ELEMEK = ["kobot, megfogó", "csavarozó egység", "asztal, adagolás", "biztonsági alrendszer", "cellavezérlés, HMI", "operátor"]
ALLOK = {  # funkció ID -> elemindexek (0-alapú)
    "1.1": [2, 5], "1.2": [0], "2.1": [2], "2.2": [0, 1], "2.3": [1], "3.1": [4], "3.2": [4, 5], "3.3": [4],
    "4.1": [3], "4.2": [0, 3], "4.3": [3, 5], "5.1": [0], "5.2": [0],
}
N = 60


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Funkciófa és allokáció – sablon", [
        "■ Mire való? A rendszer funkcióinak hierarchikus, megoldássemleges lebontása, és a funkciók hozzárendelése a forma elemeihez (alrendszer, komponens, ember, szoftver).",
        "1. A „Funkciófa” lapon minden funkció kapjon azonosítót (0, 1, 1.1, 1.1.1 …) és szülőt. A funkciót igei szerkezettel írd: tárgy + igéből képzett főnév (például „csavar adagolása”).",
        "2. A képletes oszlopok jelzik: a szintet, a gyermekek számát (2–9 között ideális), azt, ha a funkció neve nem igei szerkezetű, és azt, ha megoldásnevet tartalmaz (a „Szótár” lap listái alapján – a listákat bővítheted).",
        "3. Az „Allokáció” lapon a sorokba a legalsó szintű funkciók, az oszlopfejlécekbe a forma elemei kerülnek. Tegyél „x”-et oda, ahol az elem részt vesz a funkcióban.",
        "4. A „Gazdák száma” oszlop jelzi a gazdátlan funkciókat (elveszett funkció) és a több elemhez rendelt funkciókat (interfész keletkezik). Az alsó sor megmutatja, hány funkcióban vesz részt egy-egy elem.",
        "5. A modularitási mutató azt mutatja, a funkciók hány százalékának van pontosan egy gazdája (Ulrich: moduláris architektúrában a leképezés közel egy-egy megfeleltetés).",
        "■ Példa: a KoboCella funkciófája és allokációja (kézikönyv 8. fejezet).",
    ])
    sz = wb.create_sheet("Szótár")
    cimsor(sz, "Megoldásnevek szótára", "Ezek a szavak arra utalnak, hogy a funkció neve már egy megoldást tartalmaz. Bővítsd a saját szakterületed szavaival.")
    fejlec(sz, 4, ["Szó"], [28])
    for i in range(30):
        bemenet(sz.cell(row=5 + i, column=1), SZOTAR[i] if i < len(SZOTAR) else None)
    fejlec(sz, 4, ["Igei szerkezetre utaló végződés (szóközzel)"], [40], oszlop=3)
    for i in range(20):
        bemenet(sz.cell(row=5 + i, column=3), KEPZOK[i] if i < len(KEPZOK) else None)
    megjegyzes(sz["C4"], "A végződést a funkciónév szavainak végén keresi (a végére szóköz kerül). Például „ás ” illeszkedik az „adatátadás” szóra.")

    ws = wb.create_sheet("Funkciófa")
    cimsor(ws, "Funkciófa", "Azonosító: 0 = fő funkció; 1, 2 … = főfunkciók; 1.1, 1.2 … = részfunkciók.")
    fej = ["Azonosító", "Funkció (tárgy + igéből képzett főnév)", "Szülő azonosítója", "Szint", "Gyermekek száma",
           "Szélesség-ellenőrzés", "Igei szerkezet?", "Megoldássemleges?"]
    kepl = {
        4: lambda r: f'=IF(A{r}="","",IF(A{r}="0",0,LEN(A{r})-LEN(SUBSTITUTE(A{r},".",""))+1))',
        5: lambda r: f'=IF(A{r}="","",COUNTIF($C$5:$C${4 + N},A{r}))',
        6: lambda r: f'=IF(OR(A{r}="",E{r}=0),"",IF(E{r}>9,"túl sok gyermek: közbülső szint?",IF(E{r}=1,"egy gyermek: felesleges szint?","rendben")))',
        7: lambda r: (f'=IF(B{r}="","",IF(SUMPRODUCT((Szótár!$C$5:$C$24<>"")*ISNUMBER(SEARCH(Szótár!$C$5:$C$24,B{r}&" ")))>0,'
                      f'"igen","ellenőrizd"))'),
        8: lambda r: (f'=IF(B{r}="","",IF(SUMPRODUCT((Szótár!$A$5:$A$34<>"")*ISNUMBER(SEARCH(Szótár!$A$5:$A$34,B{r})))>0,'
                      f'"megoldásnév: fogalmazd át?","rendben"))'),
    }
    tablazat(ws, 4, fej, [11, 42, 12, 7, 11, 30, 13, 28], [list(x) for x in FA], bemeneti_oszlopok=(1, 2, 3),
             kepletek=kepl, uressor=N - len(FA))
    for r in range(5, 5 + N):
        ws.cell(row=r, column=1).number_format = "@"
        ws.cell(row=r, column=3).number_format = "@"
    szoveg(ws["J4"], "Összesítés", felkov=True)
    szoveg(ws["J5"], "Funkciók száma")
    keplet(ws["K5"], f'=COUNTIF(B5:B{4 + N},"?*")')
    szoveg(ws["J6"], "Legmélyebb szint")
    keplet(ws["K6"], f"=MAX(D5:D{4 + N})")
    szoveg(ws["J7"], "Nem igei szerkezetű nevek")
    keplet(ws["K7"], f'=COUNTIF(G5:G{4 + N},"ellenőrizd")')
    szoveg(ws["J8"], "Megoldásnevet tartalmazó funkciók")
    keplet(ws["K8"], f'=COUNTIF(H5:H{4 + N},"megoldásnév*")')
    ws.column_dimensions["J"].width = 32
    ws.column_dimensions["K"].width = 10

    al = wb.create_sheet("Allokáció")
    cimsor(al, "Allokációs táblázat", "Tegyél „x”-et oda, ahol a forma eleme részt vesz a funkció ellátásában.")
    levelek = [f for f in FA if f[0] in ALLOK]
    fejlec(al, 4, ["Azonosító", "Funkció"] + [""] * 8 + ["Gazdák száma", "Állapot"], [10, 30] + [13] * 8 + [10, 24])
    for j in range(8):
        c = al.cell(row=4, column=3 + j)
        bemenet(c, ELEMEK[j] if j < len(ELEMEK) else None)
        c.alignment = kozep
    NA = 40
    for i in range(NA):
        r = 5 + i
        f = levelek[i] if i < len(levelek) else None
        bemenet(al.cell(row=r, column=1), f[0] if f else None)
        al.cell(row=r, column=1).number_format = "@"
        bemenet(al.cell(row=r, column=2), f[1] if f else None)
        for j in range(8):
            bemenet(al.cell(row=r, column=3 + j), "x" if f and j in ALLOK[f[0]] else None)
            al.cell(row=r, column=3 + j).alignment = kozep
        keplet(al.cell(row=r, column=11), f'=IF(B{r}="","",COUNTA(C{r}:J{r}))')
        keplet(al.cell(row=r, column=12),
               f'=IF(B{r}="","",IF(K{r}=0,"nincs gazdája!",IF(K{r}=1,"egy gazda","interfész: "&K{r}&" elem")))')
    rs = 5 + NA
    szoveg(al.cell(row=rs, column=2), "Funkciók száma elemenként", felkov=True)
    for j in range(8):
        col = get_column_letter(3 + j)
        keplet(al.cell(row=rs, column=3 + j), f'=IF({col}4="","",COUNTA({col}5:{col}{rs - 1}))')
    szoveg(al.cell(row=rs + 2, column=2), "Gazdátlan funkciók", felkov=True)
    keplet(al.cell(row=rs + 2, column=3), f'=COUNTIF(K5:K{rs - 1},0)')
    szoveg(al.cell(row=rs + 3, column=2), "Interfészt létrehozó funkciók", felkov=True)
    keplet(al.cell(row=rs + 3, column=3), f'=COUNTIF(K5:K{rs - 1},">1")')
    szoveg(al.cell(row=rs + 4, column=2), "Modularitási mutató (egy gazdás funkciók aránya)", felkov=True)
    keplet(al.cell(row=rs + 4, column=3), f'=IF(COUNTIF(B5:B{rs - 1},"?*")=0,"",COUNTIF(K5:K{rs - 1},1)/COUNTIF(B5:B{rs - 1},"?*"))', "0%")
    megjegyzes(al.cell(row=rs + 4, column=3), "Ulrich (1995): moduláris architektúrában a funkcionális elemek és a fizikai komponensek közötti leképezés egy-egy megfeleltetés.")
    al.freeze_panes = "C5"
    return mentes(wb, "funkciofa_sablon.xlsx")
