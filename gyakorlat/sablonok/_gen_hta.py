"""Hierarchikus feladatelemzés (HTA) sablon (eszközlap: HTA)."""
from _kozos import *  # noqa: F401,F403

HTA = [  # id, megnevezés, szülő, terv, idő [s], gyakoriság/ciklus, ciklusidőbe számít?, hibatípus, hibalehetőség, következmény, javaslat
    ("0", "motorok szerelése a KoboCellában egy műszakon át", "", "1, majd 2 ismételve; ha hibajelzés: 3, utána vissza 2-re; a műszak végén 4", None, None, "", "", "", "", ""),
    ("1", "műszak indítása", "0", "1.1 > 1.2 > 1.3", None, None, "", "", "", "", ""),
    ("1.1", "bejelentkezés a HMI-n", "1", "", 30, None, "nem", "", "", "", ""),
    ("1.2", "típusprogram ellenőrzése", "1", "", 20, None, "nem", "tévedés", "rossz típusprogram marad betöltve", "hibás nyomaték egy teljes sorozaton", "a HMI a gyártási rendelés alapján javasolja a programot"),
    ("1.3", "csavarellátás ellenőrzése", "1", "", 40, None, "nem", "kihagyás", "az ellenőrzés elmarad", "leállás a műszak elején", "töltöttségérzékelő az adagolóban"),
    ("2", "egy motor szerelése (ciklus)", "0", "2.1 > 2.2 > 2.3 > 2.4 > 2.5", None, None, "", "", "", "", ""),
    ("2.1", "motorház kivétele a tálcáról", "2", "", 4, 1, "igen", "", "", "", ""),
    ("2.2", "motorház behelyezése a befogóba", "2", "", 6, 1, "igen", "megcsúszás", "nem ül fel teljesen a befogóra", "a kobot nem indul, időveszteség", "befogóérzékelő, HMI-visszajelzés"),
    ("2.3", "fedél ráhelyezése", "2", "", 5, 1, "igen", "megcsúszás", "fordítva helyezi fel a fedelet", "tömítetlen motor", "aszimmetrikus illesztőcsapok (poka-yoke)"),
    ("2.4", "kilépés a zónából", "2", "", 1.5, 1, "igen", "szabályszegés", "a zónában marad, hogy gyorsabb legyen", "a kobot csökkentett sebességgel dolgozik, ciklusidő-növekedés", "a lézerszkenner csak zónaelhagyás után engedi a teljes sebességet"),
    ("2.5", "indítás nyugtázása", "2", "", 1.5, 1, "igen", "", "", "", ""),
    ("3", "hibajelzés kezelése", "0", "3.1 > 3.2 > 3.3", None, None, "", "", "", "", ""),
    ("3.1", "hibakód leolvasása", "3", "", 5, None, "nem", "tévedés", "félreérti a hibakódot", "jó darab a selejtbe vagy fordítva", "a HMI a hiba helyét is mutatja"),
    ("3.2", "hibás darab a selejtdobozba", "3", "", 8, None, "nem", "kihagyás", "a hibás darab a kiadóba kerül", "hibás motor a vevőnél", "a kiadó csak a selejtdoboz érzékelőjének jelzése után enged"),
    ("3.3", "nyugtázás", "3", "", 2, None, "nem", "", "", "", ""),
    ("4", "műszak zárása", "0", "4.1 > 4.2", None, None, "", "", "", "", ""),
    ("4.1", "adatok lezárása, műszakátadás", "4", "", 60, None, "nem", "kihagyás", "nyitott eltérés nem kerül át", "a következő műszak nem tud a hibáról", "strukturált átadólap a HMI-n"),
    ("4.2", "terület rendbetétele", "4", "", 300, None, "nem", "", "", "", ""),
]
N = 60


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Hierarchikus feladatelemzés (HTA) – sablon", [
        "■ Mire való? Annak leírása, mit kell az embernek tennie egy cél eléréséhez: célok és részcélok hierarchiája tervekkel, időbecsléssel és a lehetséges hibákkal (Annett–Duncan, Stanton).",
        "1. A „HTA” lapon a 0 a fő cél. Minden részcélhoz írj tervet: milyen sorrendben és milyen feltételek mellett hajtódnak végre a gyermekei (például „2.1 > 2.2 > 2.3”, „ha hibajelzés: 3”).",
        "2. A legalsó szintű műveletekhez adj időbecslést. A ciklusonként ismétlődő műveleteknél add meg a gyakoriságot is (1 = minden ciklusban), és jelöld „igen”-nel a „Ciklusidőbe számít?” oszlopban: ezekből a lap kiszámolja a kezelő ciklusonkénti idejét, és összeveti az időkerettel. A ritka eseményeket (hibakezelés) ne számítsd a ciklusidőbe: azok a rendelkezésre állást és a teljesítménymutatókat terhelik.",
        "3. Minden művelethez gondold végig, milyen hiba fordulhat elő (Reason kategóriái: megcsúszás, kihagyás, tévedés, szabályszegés), mi a következménye, és mit javasolsz ellene.",
        "4. A lebontást ott állítsd meg, ahol a további bontás már nem ad hasznos információt az elemzés céljához.",
        "5. A HTA kirajzolását és a kezelő–gép idődiagramot a hta notebook készíti el.",
        "■ Példa: a KoboCella kezelőjének feladatai egy műszakon át (kézikönyv 11. fejezet).",
    ])
    ws = wb.create_sheet("HTA")
    cimsor(ws, "Hierarchikus feladatelemzés")
    szoveg(ws["A3"], "A kezelő időkerete ciklusonként [s]:", felkov=True)
    bemenet(ws["D3"], 18)
    fej = ["Azonosító", "Részcél vagy művelet", "Szülő", "Terv (részcélnál)", "Idő [s]", "Gyakoriság ciklusonként",
           "Ciklusidőbe számít?", "Szint", "Idő ciklusonként [s]", "Hibatípus", "Lehetséges hiba", "Következmény", "Javaslat"]
    kepl = {8: lambda r: f'=IF(A{r}="","",IF(A{r}="0",0,LEN(A{r})-LEN(SUBSTITUTE(A{r},".",""))+1))',
            9: lambda r: f'=IF(OR(G{r}<>"igen",E{r}="",F{r}=""),"",E{r}*F{r})'}
    sor = [[a, b, c, d, e, f, g, None, None, h, i, j, k] for a, b, c, d, e, f, g, h, i, j, k in HTA]
    u = tablazat(ws, 5, fej, [10, 34, 9, 30, 8, 12, 12, 7, 12, 14, 30, 30, 34], sor,
                 bemeneti_oszlopok=(1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13), kepletek=kepl, uressor=N - len(sor),
                 formatumok={5: "0.0", 6: "0.000", 9: "0.00"})
    for r in range(6, u + 1):
        ws.cell(row=r, column=1).number_format = "@"
        ws.cell(row=r, column=3).number_format = "@"
    legordulo(ws, f"G6:G{u}", ["igen", "nem"])
    legordulo(ws, f"J6:J{u}", ["megcsúszás", "kihagyás", "tévedés", "szabályszegés"])
    rr = u + 2
    for k_, (t, f, fmt) in enumerate([
            ("A kezelő ideje ciklusonként [s]", f"=SUM(I6:I{u})", "0.00"),
            ("Tartalék az időkerethez képest [s]", f"=D3-B{rr}", "+0.00;-0.00;0.00"),
            ("Műveletek száma (idővel)", f"=COUNT(E6:E{u})", "0"),
            ("Azonosított hibalehetőségek", f'=COUNTIF(J6:J{u},"?*")', "0"),
            ("Ebből megcsúszás / kihagyás / tévedés / szabályszegés",
             f'=COUNTIF(J6:J{u},"megcsúszás")&" / "&COUNTIF(J6:J{u},"kihagyás")&" / "&COUNTIF(J6:J{u},"tévedés")&" / "&COUNTIF(J6:J{u},"szabályszegés")', None)]):
        szoveg(ws.cell(row=rr + k_, column=1), t, felkov=True)
        ws.merge_cells(start_row=rr + k_, start_column=1, end_row=rr + k_, end_column=1)
        keplet(ws.cell(row=rr + k_, column=2), f, fmt, True)
    ws.column_dimensions["A"].width = 30
    ws.freeze_panes = "C6"
    return mentes(wb, "hta_sablon.xlsx")
