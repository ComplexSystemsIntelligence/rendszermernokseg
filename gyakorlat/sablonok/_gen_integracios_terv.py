"""Integrációs terv és interfészjegyzék (eszközlap: Integrációs terv és interfészmátrix)."""
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation

from _kozos import *  # noqa: F401,F403

NE, NI, NL, RACS = 15, 30, 20, 30

ELEMEK = [
    ("Cellavezérlés (PLC)", "hardver és szoftver", 1, "robotintegrátor"),
    ("Biztonsági vezérlés", "hardver", 1, "biztonsági mérnök"),
    ("Lézerszkenner", "hardver", 1, "biztonsági mérnök"),
    ("Üzem (energia, környezet)", "környezet", 1, "karbantartás"),
    ("Kobot", "hardver és szoftver", 2, "robotintegrátor"),
    ("Csavarozó orsó", "hardver", 3, "robotintegrátor"),
    ("Csavaradagoló", "hardver", 3, "robotintegrátor"),
    ("Csavarozó vezérlő", "hardver és szoftver", 3, "beszállító"),
    ("Befogó készülék", "hardver", 4, "gyártástechnológus"),
    ("Motorház (munkadarab)", "anyag", 4, "gyártástechnológus"),
    ("Kezelőfelület (HMI)", "szoftver", 5, "rendszermérnök"),
    ("Kezelő", "ember", 5, "ergonómus"),
    ("MES", "szoftver", 6, "informatika"),
]

INTERFESZEK = [
    ("I-01", "Kobot", "Csavarozó orsó", "kétirányú", "mechanikai, energetikai, jel", "rögzítés, tömeg, 24 V, indítás/kész", "ICD-01", "jóváhagyott", "robotintegrátor", 3, 3),
    ("I-02", "Csavaradagoló", "Csavarozó orsó", "A→B", "mechanikai, pneumatikus", "csavar, sűrített levegő", "ICD-02", "jóváhagyott", "robotintegrátor", 2, 3),
    ("I-03", "Kobot", "Cellavezérlés (PLC)", "kétirányú", "jel, adat", "indítás, kész, hibakód", "ICD-03", "jóváhagyott", "robotintegrátor", 3, 2),
    ("I-04", "Lézerszkenner", "Biztonsági vezérlés", "A→B", "biztonsági jel", "védőmező megsértése", "ICD-04", "jóváhagyott", "biztonsági mérnök", 5, 1),
    ("I-05", "Befogó készülék", "Motorház (munkadarab)", "kétirányú", "mechanikai", "pozicionálás, rögzítés", "ICD-05", "jóváhagyott", "gyártástechnológus", 3, 4),
    ("I-06", "Kezelő", "Kezelőfelület (HMI)", "kétirányú", "ember–gép", "utasítás, hibajelzés, nyugtázás", "ICD-06", "jóváhagyott", "ergonómus", 4, 5),
    ("I-07", "Csavarozó vezérlő", "MES", "A→B", "adat", "nyomaték, szög, megfelelő/nem megfelelő, ciklusidő", "ICD-07", "tervezet", "informatika, beszállító", 4, 6),
    ("I-08", "Üzem (energia, környezet)", "Cellavezérlés (PLC)", "A→B", "energetikai, környezeti", "400 V, sűrített levegő, padló, hőmérséklet", "ICD-08", "jóváhagyott", "karbantartás", 2, 1),
    ("I-09", "Biztonsági vezérlés", "Kobot", "A→B", "biztonsági jel", "védett leállítás, sebességcsökkentés", "ICD-09", "jóváhagyott", "biztonsági mérnök", 5, 2),
    ("I-10", "Biztonsági vezérlés", "Cellavezérlés (PLC)", "kétirányú", "jel", "biztonsági állapot, nyugtázás", "ICD-10", "jóváhagyott", "biztonsági mérnök", 4, 1),
    ("I-11", "Csavarozó vezérlő", "Cellavezérlés (PLC)", "kétirányú", "jel, adat", "programválasztás, indítás, megfelelő/nem megfelelő", "ICD-11", "jóváhagyott", "robotintegrátor", 3, 3),
    ("I-12", "Befogó készülék", "Cellavezérlés (PLC)", "A→B", "jel", "darabjelenlét, rögzítve", "ICD-12", "jóváhagyott", "gyártástechnológus", 2, 4),
    ("I-13", "Kezelőfelület (HMI)", "Cellavezérlés (PLC)", "kétirányú", "adat", "állapot, parancsok, hibaüzenetek", "ICD-13", "jóváhagyott", "rendszermérnök", 3, 5),
    ("I-14", "Csavarozó vezérlő", "Csavarozó orsó", "kétirányú", "energetikai, jel", "motoráram, szöghelyzet-jeladó", "ICD-14", "jóváhagyott", "beszállító", 2, 3),
]

LEPESEK = [
    (1, "Vezérlés és biztonsági áramkör", "cellavezérlés, biztonsági vezérlés, lézerszkenner, üzemi betáplálás", "I/O-szimulátor a még hiányzó jeladók helyett", "T1: vészleállítás, védőmező, biztonsági állapot", "biztonsági mérnök", None, None, 3),
    (2, "Kobot", "kobot", "tömegpróbatest a csavarozó orsó helyett (csonk); offline robotprogram", "T2: mozgás, kommunikáció, védett leállítás", "robotintegrátor", 1, None, 3),
    (3, "Csavarozó orsó, adagoló, vezérlő", "csavarozó orsó, csavaradagoló, csavarozó vezérlő", "kalibrált nyomatékmérő, próbadarab", "T3: nyomaték és szög", "robotintegrátor", 2, None, 4),
    (4, "Befogó készülék, érzékelők", "befogó készülék, motorház", "mintadarabok a tűrésmező két szélén", "T4: pozicionálás, darabjelenlét", "gyártástechnológus", 3, None, 2),
    (5, "Kezelőfelület", "kezelőfelület, kezelő", "kezelői próbaforgatókönyv", "T5: kezelői feladatok próbája", "ergonómus", 2, None, 3),
    (6, "MES-kapcsolat", "MES", "MES-tesztpéldány", "T6: adatátvitel", "informatika", 4, 5, 2),
    (7, "Gyári átvételi teszt (FAT)", "–", "–", "FAT: ciklusidő, minőség, biztonság", "projektvezető", 6, None, 2),
    (8, "Bontás, szállítás, telepítés", "–", "–", "telepítés utáni bekötési ellenőrzés", "robotintegrátor, karbantartás", 7, None, 4),
    (9, "Helyszíni átvételi teszt (SAT)", "–", "–", "SAT: háromműszakos próbaüzem", "projektvezető", 8, None, 3),
]


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Integrációs terv és interfészjegyzék – sablon", [
        "■ Mire való? Az integráció megtervezése: az elemek és interfészeik nyilvántartása, az N²-mátrix, az integrációs lépések "
        "(mi kerül össze, milyen segédeszközzel, milyen teszt zárja, ki a felelős), az ütemezés és a terv ellenőrzése.",
        "■ Elemek: sorold fel a rendszer elemeit (legfeljebb 15), és add meg, melyik integrációs lépésben kerülnek a rendszerbe.",
        "■ Interfészek: legfeljebb 30 interfész. Az A és B elemet a listából válaszd (az Elemek lapról). Az irány az N²-mátrixban "
        "a sor (kimenet) és az oszlop (bemenet) helyét határozza meg. Add meg az ICD állapotát, a kockázatot (1–5) és azt a lépést, "
        "amelynek tesztje az interfészt ellenőrzi. Az Ellenőrzés oszlop jelzi, ha az interfész nincs lépéshez rendelve, ha olyan "
        "lépésben ellenőriznéd, amikor valamelyik eleme még nincs a rendszerben, vagy ha az ICD még nincs jóváhagyva.",
        "■ N2: az N²-mátrix automatikusan készül. Az átlóban az elemek, a sor és az oszlop kereszteződésében a sor elemétől az oszlop "
        "eleméhez haladó interfészek száma áll.",
        "■ Lépések: legfeljebb 20 lépés (az átvételi tesztek, a szállítás és a telepítés is lépés). Az előzmény csak korábbi sorban álló "
        "lépés lehet. A kezdés és a befejezés munkanapban számolódik, az időrács 30 napot mutat.",
        "■ Összesítés: a terv ellenőrzésének eredménye és a lépésenkénti interfészszám és kockázat.",
        "A kitöltött példa a KoboCella integrációja (kézikönyv 22. fejezet). A kézikönyv nyolc fő interfészét a részletes tervezés során "
        "a cellavezérlés hat belső kapcsolatával egészítettük ki (I-09–I-14).",
        "Források: ISO/IEC/IEEE 15288:2023, 6.4.8.; INCOSE SE Handbook (2023); Eppinger és Browning (2012); NASA Systems Engineering Handbook (2016), 5.2. szakasz és H függelék.",
    ])

    # ---- Elemek
    ws = wb.create_sheet("Elemek")
    cimsor(ws, "Rendszerelemek", "Melyik lépésben kerül az elem a rendszerbe?")
    tablazat(ws, 4, ["Elem", "Típus", "Integrálva a lépésben", "Felelős"], [30, 22, 14, 22],
             [list(e) for e in ELEMEK], bemeneti_oszlopok=(1, 2, 3, 4), uressor=NE - len(ELEMEK))
    legordulo(ws, "B5:B19", ["hardver", "szoftver", "hardver és szoftver", "ember", "anyag", "környezet"])
    ws.freeze_panes = "A5"
    elem_rng = "Elemek!$A$5:$A$19"
    lepes_rng = "Elemek!$C$5:$C$19"

    # ---- Interfészek
    ws = wb.create_sheet("Interfészek")
    cimsor(ws, "Interfészjegyzék", "Az irány az N²-mátrixban: A→B esetén a sor az A, az oszlop a B elem.")
    fej = ["Azonosító", "A elem", "B elem", "Irány", "Típus", "Mi halad át?", "Dokumentum (ICD)", "ICD állapota",
           "Felelős", "Kockázat (1–5)", "Ellenőrző lépés", "Legkorábbi lépés", "Ellenőrzés"]

    def legkorabbi(r):
        return (f'=IF(OR(B{r}="",C{r}=""),"",MAX(IFERROR(INDEX({lepes_rng},MATCH(B{r},{elem_rng},0)),0),'
                f'IFERROR(INDEX({lepes_rng},MATCH(C{r},{elem_rng},0)),0)))')

    def ellenorzes(r):
        return (f'=IF(A{r}="","",IF(OR(ISNA(MATCH(B{r},{elem_rng},0)),ISNA(MATCH(C{r},{elem_rng},0))),"ismeretlen elem",'
                f'IF(K{r}="","nincs lépéshez rendelve",IF(K{r}<L{r},"túl korai lépés",'
                f'IF(H{r}<>"jóváhagyott","ICD nincs jóváhagyva","rendben")))))')

    utolso = tablazat(ws, 4, fej, [10, 24, 24, 11, 22, 32, 12, 13, 20, 10, 10, 10, 22],
                      [list(i) for i in INTERFESZEK], bemeneti_oszlopok=tuple(range(1, 12)),
                      kepletek={12: legkorabbi, 13: ellenorzes}, uressor=NI - len(INTERFESZEK))
    for oszlop in ("B", "C"):
        dv = DataValidation(type="list", formula1=f"={elem_rng}", allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{oszlop}5:{oszlop}{utolso}")
    legordulo(ws, f"D5:D{utolso}", ["A→B", "B→A", "kétirányú"])
    legordulo(ws, f"H5:H{utolso}", ["nincs", "tervezet", "jóváhagyott"])
    legordulo(ws, f"J5:J{utolso}", ["1", "2", "3", "4", "5"])
    piros = PatternFill("solid", fgColor="F6D5D5")
    ws.conditional_formatting.add(f"M5:M{utolso}", FormulaRule(formula=['AND(M5<>"",M5<>"rendben")'], fill=piros))
    megjegyzes(ws["J4"], "1: egyszerű, ismert megoldás; 5: új, összetett vagy biztonsági interfész, két beszállító között.")
    megjegyzes(ws["L4"], "A két elem közül a később integrált elem lépése: ennél korábban az interfész nem ellenőrizhető.")
    ws.freeze_panes = "B5"
    I_UT = utolso

    # ---- N2
    ws = wb.create_sheet("N2")
    cimsor(ws, "N²-mátrix", "Átló: az elemek. Sor: kimenet, oszlop: bemenet. A cellában a sor elemétől az oszlop eleméhez haladó interfészek száma.")
    ws.column_dimensions["A"].width = 5
    for k in range(NE):
        c = ws.cell(row=4, column=2 + k, value=k + 1)
        c.font, c.fill, c.alignment, c.border = fej_font, fej_fill, kozep, keret
        ws.column_dimensions[get_column_letter(2 + k)].width = 11
    for i in range(NE):
        r = 5 + i
        c = ws.cell(row=r, column=1, value=i + 1)
        c.font, c.fill, c.alignment, c.border = fej_font, fej_fill, kozep, keret
        ws.row_dimensions[r].height = 40
        for j in range(NE):
            c = ws.cell(row=r, column=2 + j)
            if i == j:
                c.value = f'=IF(INDEX({elem_rng},{i + 1})="","",INDEX({elem_rng},{i + 1}))'
                c.font = Font(name=BETU, size=8, bold=True, color="FFFFFF")
                c.fill = PatternFill("solid", fgColor="1F3F5E")
            else:
                ri, cj = f"INDEX({elem_rng},{i + 1})", f"INDEX({elem_rng},{j + 1})"
                c.value = (f"=IF(OR({ri}=\"\",{cj}=\"\"),\"\","
                           f"COUNTIFS('Interfészek'!$B$5:$B${I_UT},{ri},'Interfészek'!$C$5:$C${I_UT},{cj},'Interfészek'!$D$5:$D${I_UT},\"<>B→A\")"
                           f"+COUNTIFS('Interfészek'!$C$5:$C${I_UT},{ri},'Interfészek'!$B$5:$B${I_UT},{cj},'Interfészek'!$D$5:$D${I_UT},\"<>A→B\"))")
                c.font = Font(name=BETU, size=11, bold=True, color=KEK)
                c.number_format = '0;-0;;@'
                c.fill = keplet_fill
            c.alignment, c.border = kozep, keret
    ws.conditional_formatting.add(f"B5:{get_column_letter(1 + NE)}{4 + NE}",
                                  CellIsRule(operator="greaterThan", formula=["0"], fill=PatternFill("solid", fgColor="F4D9A8")))
    szoveg(ws.cell(row=6 + NE, column=1), "Olvasat: a sárga cellák jelzik a kapcsolatokat. A sok kapcsolattal rendelkező elem "
           "(itt a cellavezérlés) korai integrálása mellett szól, hogy a többi elem rá épül.")
    ws.merge_cells(start_row=6 + NE, start_column=1, end_row=6 + NE, end_column=1 + NE)

    # ---- Lépések
    ws = wb.create_sheet("Lépések")
    cimsor(ws, "Integrációs lépések és ütemezés", "Az előzmény csak korábbi sorban álló lépés lehet. Időegység: munkanap.")
    fej = ["Lépés", "Megnevezés", "Hozzáadott elemek", "Interfészek", "Kockázat", "Segédeszköz (csonk, meghajtó, szimulátor)",
           "Lezáró teszt", "Felelős", "Előzmény 1", "Előzmény 2", "Időtartam [nap]", "Kezdés", "Befejezés", "Állapot"]
    I_K = f"'Interfészek'!$K$5:$K${I_UT}"
    I_J = f"'Interfészek'!$J$5:$J${I_UT}"

    def kezdes(r):
        if r == 5:
            return f'=IF(A{r}="","",0)'
        return (f'=IF(A{r}="","",MAX(IFERROR(INDEX($M$5:M{r - 1},MATCH(I{r},$A$5:A{r - 1},0)),0),'
                f'IFERROR(INDEX($M$5:M{r - 1},MATCH(J{r},$A$5:A{r - 1},0)),0)))')

    sorok = [[l[0], l[1], l[2], None, None, l[3], l[4], l[5], l[6], l[7], l[8], None, None, "tervezett"] for l in LEPESEK]
    utolso = tablazat(ws, 4, fej, [7, 26, 30, 10, 9, 30, 30, 18, 9, 9, 9, 8, 9, 12], sorok,
                      bemeneti_oszlopok=(1, 2, 3, 6, 7, 8, 9, 10, 11, 14),
                      kepletek={4: lambda r: f'=IF(A{r}="","",COUNTIF({I_K},A{r}))',
                                5: lambda r: f'=IF(A{r}="","",SUMIF({I_K},A{r},{I_J}))',
                                12: kezdes,
                                13: lambda r: f'=IF(A{r}="","",L{r}+K{r})'},
                      uressor=NL - len(LEPESEK), formatumok={11: "0.0", 12: "0.0", 13: "0.0"})
    legordulo(ws, f"N5:N{utolso}", ["tervezett", "folyamatban", "kész", "megismételve"])
    o0 = 15
    for k in range(RACS):
        c = ws.cell(row=4, column=o0 + k, value=k + 1)
        c.font, c.fill, c.alignment, c.border = fej_font, fej_fill, kozep, keret
        ws.column_dimensions[get_column_letter(o0 + k)].width = 3.2
        for r in range(5, utolso + 1):
            c = ws.cell(row=r, column=o0 + k)
            c.value = f'=IF($A{r}="","",IF(AND({k + 1}>$L{r},{k + 1}<=$M{r}),1,""))'
            c.number_format = ";;;"
            c.border = keret
    ws.conditional_formatting.add(f"{get_column_letter(o0)}5:{get_column_letter(o0 + RACS - 1)}{utolso}",
                                  FormulaRule(formula=[f"{get_column_letter(o0)}5=1"], fill=PatternFill("solid", fgColor=KEK)))
    szoveg(ws.cell(row=utolso + 2, column=2), "Teljes időtartam [munkanap]", felkov=True)
    keplet(ws.cell(row=utolso + 2, column=3), f"=MAX(M5:M{utolso})", "0.0", felkov=True)
    ws.freeze_panes = "C5"
    L_UT = utolso

    # ---- Összesítés
    ws = wb.create_sheet("Összesítés")
    cimsor(ws, "A terv ellenőrzése", "Minden interfészt egy lépés tesztje ellenőrizzen, és az ICD a lépés előtt legyen jóváhagyva.")
    ws.column_dimensions["A"].width = 46
    ws.column_dimensions["B"].width = 14
    I = "'Interfészek'!"
    mutatok = [
        ("Elemek száma", f"=COUNTA(Elemek!A5:A19)", "0"),
        ("Lépéshez nem rendelt elemek", f'=COUNTA(Elemek!A5:A19)-COUNT(Elemek!C5:C19)', "0"),
        ("Interfészek száma", f"=COUNTA({I}A5:A{I_UT})", "0"),
        ("Lépéshez rendelt interfészek", f"=COUNT({I}K5:K{I_UT})", "0"),
        ("Jóváhagyott ICD", f'=COUNTIF({I}H5:H{I_UT},"jóváhagyott")', "0"),
        ("Rendben lévő interfészek", f'=COUNTIF({I}M5:M{I_UT},"rendben")', "0"),
        ("Figyelmeztetések", f"=B6-B9", "0"),
        ("A terv lefedettsége (rendben / összes)", f'=IF(B6=0,"",B9/B6)', "0%"),
        ("Integrációs kockázat összesen", f"=SUM({I}J5:J{I_UT})", "0"),
        ("Teljes időtartam [munkanap]", f"=MAX('Lépések'!M5:M{L_UT})", "0.0"),
    ]
    fejlec(ws, 3, ["Mutató", "Érték"])
    for i, (nev, f, fmt) in enumerate(mutatok):
        szoveg(ws.cell(row=4 + i, column=1), nev)
        keplet(ws.cell(row=4 + i, column=2), f, fmt, felkov=True)
    ws.conditional_formatting.add("B10:B10", CellIsRule(operator="greaterThan", formula=["0"], fill=piros))

    s0 = 17
    szoveg(ws.cell(row=s0 - 1, column=1), "Lépésenként", felkov=True)
    fejlec(ws, s0, ["Lépés", "Interfészek", "Kockázat"], oszlop=1)
    ws.column_dimensions["C"].width = 12
    for i in range(NL):
        r = s0 + 1 + i
        lr = 5 + i
        keplet(ws.cell(row=r, column=1), f"=IF('Lépések'!A{lr}=\"\",\"\",'Lépések'!A{lr}&\". \"&'Lépések'!B{lr})")
        keplet(ws.cell(row=r, column=2), f"=IF('Lépések'!A{lr}=\"\",\"\",'Lépések'!D{lr})", "0")
        keplet(ws.cell(row=r, column=3), f"=IF('Lépések'!A{lr}=\"\",\"\",'Lépések'!E{lr})", "0")
    ch = BarChart()
    ch.type = "col"
    diagram_kozos(ch, "Ellenőrzött interfészek és kockázat lépésenként", "lépés", "darab, pontszám", szel=20, mag=9)
    ch.add_data(Reference(ws, min_col=2, max_col=3, min_row=s0, max_row=s0 + len(LEPESEK)), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=s0 + 1, max_row=s0 + len(LEPESEK)))
    ws.add_chart(ch, "E3")
    szoveg(ws.cell(row=s0 + NL + 2, column=1),
           "Olvasat: a sok interfészt és nagy kockázatot hordozó lépés hibakeresése a legnehezebb; ha lehet, bontsd két lépésre, "
           "vagy készíts hozzá segédeszközt (csonk, szimulátor). Az egyszerre integrálás egyetlen lépésben ellenőrizné az összes interfészt.")
    return mentes(wb, "integracios_terv_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
