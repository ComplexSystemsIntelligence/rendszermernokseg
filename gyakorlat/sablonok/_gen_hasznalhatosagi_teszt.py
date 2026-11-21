"""Használhatósági teszt tervezése és kiértékelése (eszközlap: Használhatósági teszt)."""
from openpyxl.formatting.rule import CellIsRule, FormulaRule

from _kozos import *  # noqa: F401,F403

NP, NF, NU = 30, 8, 30

RESZTVEVOK = [
    ("P01", "turista", "nem regisztrált", 62.5), ("P02", "egyetemista", "", 72.5), ("P03", "gyengénlátó", "nagyító funkció", 52.5),
    ("P04", "turista", "nem regisztrált", 60.0), ("P05", "egyetemista", "", 80.0), ("P06", "gyengénlátó", "képernyőolvasó", 47.5),
    ("P07", "idősebb lakó", "ritkán használ alkalmazást", 45.0), ("P08", "egyetemista", "", 75.0), ("P09", "idősebb lakó", "", 57.5),
    ("P10", "turista", "angol nyelvű", 70.0), ("P11", "gyengénlátó", "nagyító funkció", 55.0), ("P12", "idősebb lakó", "", 90.0),
]

FELADATOK = [
    ("F1", "Kölcsönzés regisztrált felhasználóként", "A kerékpár kiold, a kölcsönzés elindul.", 90),
    ("F2", "Dokkoló keresése szabad hellyel a térképen", "A résztvevő megnevezi a legközelebbi, szabad hellyel rendelkező dokkolót.", 60),
    ("F3", "Kölcsönzés vendégként, regisztráció nélkül", "A kerékpár kiold; segítség nélkül, legfeljebb 3 perc alatt.", 180),
    ("F4", "Visszaadás", "A kerékpár rögzül, a kölcsönzés lezárul, a résztvevő látja a díjat.", 60),
]

SIKER = [[1, 1, 0, 1], [1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 0, 1], [1, 1, 1, 1], [1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 1, 1],
         [1, 1, 0, 0], [1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]
IDO = [[74, 48, None, 41], [52, 35, 150, 30], [96, None, None, 58], [81, 55, None, 47], [48, 31, 131, 28], [118, None, None, 66],
       [None, 71, None, 62], [57, 38, 162, 33], [102, 64, None, None], [69, 44, 174, 39], [91, None, None, 52], [88, 60, 196, 49]]

PROBLEMAK = [
    ("U1", "Vendégfizetésnél a kártyaadatok megadása után nem egyértelmű a következő lépés.", "F3", "súlyos", ["P01", "P03", "P04", "P06", "P07", "P11"]),
    ("U2", "A dokkolók szabad helyeit a térkép csak színnel jelöli.", "F2", "súlyos", ["P03", "P06", "P11"]),
    ("U3", "Teli állomásnál nincs javaslat a legközelebbi szabad helyre.", "F4", "közepes", ["P02", "P05", "P09", "P12"]),
    ("U4", "A dokkoló zárását csak hangjelzés igazolja vissza.", "F4", "közepes", ["P04", "P07", "P10"]),
    ("U5", "A díj csak a fizetés után látszik.", "F3", "közepes", ["P01", "P02", "P04", "P05", "P08", "P10", "P12"]),
    ("U6", "A Kölcsönzés gomb kontrasztja alacsony.", "F1", "kisebb", ["P03", "P11"]),
    ("U7", "A térkép nagyításakor eltűnnek az állomásnevek.", "F2", "kisebb", ["P02", "P06", "P09"]),
    ("U8", "A nyelvváltás a beállítások között rejtve van.", "F3", "kisebb", ["P10"]),
]


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Használhatósági teszt – sablon", [
        "■ Mire való? Egy használhatósági teszt tervezése és kiértékelése az ISO 9241-11 szerint: hatásosság (feladatsiker), "
        "hatékonyság (idő), elégedettség (SUS), valamint a feltárt problémák és a problémafeltárás becsült teljessége.",
        "■ Résztvevők: legfeljebb 30 fő, felhasználói csoporttal és SUS-pontszámmal (a SUS kiszámítása a NASA-TLX és SUS sablonnal).",
        "■ Feladatok: legfeljebb 8 feladat, a működési forgatókönyvekből; mindegyikhez sikerkritérium és célidő.",
        "■ Eredmények: résztvevőnként és feladatonként siker (1 = segítség nélkül befejezte, 0 = nem) és idő másodpercben; "
        "az időt csak sikeres feladatnál írd be.",
        "■ Problémák: legfeljebb 30 probléma súlyossággal; a résztvevők oszlopaiba 1-et írj, ha az adott résztvevőnél jelentkezett.",
        "■ Összesítés: feladatonkénti sikerarány módosított Wald-intervallummal (Agresti–Coull), az idők mértani átlaga, a célidőn belüli "
        "arány, a SUS átlaga t-intervallummal, a problémák észlelési valószínűsége (p) és a feltárt hányad becslése: 1 − (1 − p)^n.",
        "A kitöltött példa a VárosiBringa kölcsönző alkalmazásának első prototípusa, 12 résztvevővel (kézikönyv 11. és 24. fejezet).",
        "Források: ISO 9241-11:2018; Brooke (1996); Nielsen és Landauer (1993); Agresti és Coull (1998); Sauro és Lewis (2016).",
    ])

    # ---- Résztvevők
    ws = wb.create_sheet("Résztvevők")
    cimsor(ws, "Résztvevők", "A résztvevők a felhasználói népességet képviseljék, minden csoportból.")
    ut = tablazat(ws, 4, ["Azonosító", "Felhasználói csoport", "Megjegyzés", "SUS-pontszám"], [11, 20, 28, 13],
                  [list(r) for r in RESZTVEVOK], bemeneti_oszlopok=(1, 2, 3, 4), uressor=NP - len(RESZTVEVOK),
                  formatumok={4: "0.0"})
    ws.freeze_panes = "A5"
    R_UT = ut

    # ---- Feladatok
    ws = wb.create_sheet("Feladatok")
    cimsor(ws, "Feladatok", "A feladatok a működési forgatókönyvekből származnak; a sikerkritériumot és a célidőt előre rögzítsd.")
    tablazat(ws, 4, ["Azonosító", "Feladat", "Sikerkritérium", "Célidő [s]"], [10, 40, 56, 11],
             [list(f) for f in FELADATOK], bemeneti_oszlopok=(1, 2, 3, 4), uressor=NF - len(FELADATOK))

    # ---- Eredmények
    ws = wb.create_sheet("Eredmények")
    cimsor(ws, "Eredmények", "Siker: 1 = segítség nélkül befejezte, 0 = nem. Időt csak sikeres feladatnál írj.")
    ws.column_dimensions["A"].width = 11
    c = ws.cell(row=4, column=1, value="Résztvevő")
    c.font, c.fill, c.alignment, c.border = fej_font, fej_fill, kozep, keret
    ws.merge_cells(start_row=4, start_column=1, end_row=5, end_column=1)
    for k in range(NF):
        c1, c2 = 2 + 2 * k, 3 + 2 * k
        c = ws.cell(row=4, column=c1, value=f"='Feladatok'!A{5 + k}&\"\"")
        c.font, c.fill, c.alignment, c.border = fej_font, fej_fill, kozep, keret
        ws.merge_cells(start_row=4, start_column=c1, end_row=4, end_column=c2)
        for cc, t in ((c1, "siker"), (c2, "idő [s]")):
            x = ws.cell(row=5, column=cc, value=t)
            x.font, x.fill, x.alignment, x.border = fej_font, fej_fill, kozep, keret
            ws.column_dimensions[get_column_letter(cc)].width = 7
    sc = 2 + 2 * NF
    x = ws.cell(row=4, column=sc, value="Sikerarány")
    x.font, x.fill, x.alignment, x.border = fej_font, fej_fill, kozep, keret
    ws.merge_cells(start_row=4, start_column=sc, end_row=5, end_column=sc)
    ws.column_dimensions[get_column_letter(sc)].width = 11
    for i in range(NP):
        r = 6 + i
        keplet(ws.cell(row=r, column=1), f"=IF('Résztvevők'!A{5 + i}=\"\",\"\",'Résztvevők'!A{5 + i})")
        for k in range(NF):
            s_ = SIKER[i][k] if i < len(SIKER) and k < len(FELADATOK) else None
            t_ = IDO[i][k] if i < len(IDO) and k < len(FELADATOK) else None
            bemenet(ws.cell(row=r, column=2 + 2 * k), s_, "0")
            bemenet(ws.cell(row=r, column=3 + 2 * k), t_, "0")
        sikerek = ",".join(f"{get_column_letter(2 + 2 * k)}{r}" for k in range(NF))
        keplet(ws.cell(row=r, column=sc), f'=IF(COUNT({sikerek})=0,"",SUM({sikerek})/COUNT({sikerek}))', "0%")
    legordulo(ws, f"B6:{get_column_letter(1 + 2 * NF)}{5 + NP}", ["1", "0"])
    ws.freeze_panes = "B6"
    E_UT = 5 + NP

    # ---- Problémák
    ws = wb.create_sheet("Problémák")
    cimsor(ws, "Feltárt problémák", "A résztvevő oszlopába 1, ha a problémával találkozott.")
    fej = ["Azonosító", "Leírás", "Feladat", "Súlyosság"] + [f"='Résztvevők'!A{5 + j}&\"\"" for j in range(NP)] + ["Észlelések", "Arány"]
    fejlec(ws, 4, fej, [8, 46, 8, 11] + [5] * NP + [10, 9])
    for i in range(NU):
        r = 5 + i
        if i < len(PROBLEMAK):
            az, le, fe, su, kik = PROBLEMAK[i]
            ertekek = [az, le, fe, su]
        else:
            kik, ertekek = [], [None] * 4
        for j, v in enumerate(ertekek):
            bemenet(ws.cell(row=r, column=1 + j), v)
        for j in range(NP):
            pid = RESZTVEVOK[j][0] if j < len(RESZTVEVOK) else None
            bemenet(ws.cell(row=r, column=5 + j), 1 if pid in kik else None, "0")
        p0, p1 = get_column_letter(5), get_column_letter(4 + NP)
        keplet(ws.cell(row=r, column=5 + NP), f'=IF(A{r}="","",SUM({p0}{r}:{p1}{r}))', "0")
        keplet(ws.cell(row=r, column=6 + NP), f"=IF(A{r}=\"\",\"\",IF('Összesítés'!$B$5=0,\"\",{get_column_letter(5 + NP)}{r}/'Összesítés'!$B$5))", "0%")
    legordulo(ws, f"D5:D{4 + NU}", ["kritikus", "súlyos", "közepes", "kisebb"])
    ws.conditional_formatting.add(f"E5:{get_column_letter(4 + NP)}{4 + NU}",
                                  CellIsRule(operator="equal", formula=["1"], fill=PatternFill("solid", fgColor="F4D9A8")))
    ws.freeze_panes = "C5"
    U_UT = 4 + NU
    EL = get_column_letter(5 + NP)

    # ---- Összesítés
    ws = wb.create_sheet("Összesítés")
    cimsor(ws, "Összesítés", "Hatásosság, hatékonyság, elégedettség és a problémafeltárás teljessége.")
    ws.column_dimensions["A"].width = 44
    for k, w in zip("BCDEFGHIJ", [11, 11, 11, 11, 11, 11, 13, 13, 13]):
        ws.column_dimensions[k].width = w
    szoveg(ws["A4"], "Konfidenciaszint", felkov=True)
    bemenet(ws["B4"], 0.95, "0%")
    szoveg(ws["A5"], "Résztvevők száma")
    keplet(ws["B5"], f"=COUNTA('Résztvevők'!A5:A{R_UT})", "0", felkov=True)
    szoveg(ws["A6"], "z-érték")
    keplet(ws["B6"], "=NORMSINV(1-(1-B4)/2)", "0.000")

    h0 = 8
    fejlec(ws, h0, ["Feladat", "Próbálkozás", "Sikeres", "Sikerarány", "Alsó határ", "Felső határ", "Célidő [s]",
                    "Idő mértani átlaga [s]", "Célidőn belül"])
    for k in range(NF):
        r = h0 + 1 + k
        sc_, tc_ = get_column_letter(2 + 2 * k), get_column_letter(3 + 2 * k)
        S = f"'Eredmények'!{sc_}6:{sc_}{E_UT}"
        T = f"'Eredmények'!{tc_}6:{tc_}{E_UT}"
        keplet(ws.cell(row=r, column=1), f"=IF('Feladatok'!A{5 + k}=\"\",\"\",'Feladatok'!A{5 + k}&\" \"&'Feladatok'!B{5 + k})")
        keplet(ws.cell(row=r, column=2), f'=IF(A{r}="","",COUNT({S}))', "0")
        keplet(ws.cell(row=r, column=3), f'=IF(A{r}="","",SUM({S}))', "0")
        keplet(ws.cell(row=r, column=4), f'=IF(OR(A{r}="",B{r}=0),"",C{r}/B{r})', "0%")
        pt = f"((C{r}+$B$6^2/2)/(B{r}+$B$6^2))"
        hw = f"($B$6*SQRT({pt}*(1-{pt})/(B{r}+$B$6^2)))"
        keplet(ws.cell(row=r, column=5), f'=IF(OR(A{r}="",B{r}=0),"",MAX(0,{pt}-{hw}))', "0%")
        keplet(ws.cell(row=r, column=6), f'=IF(OR(A{r}="",B{r}=0),"",MIN(1,{pt}+{hw}))', "0%")
        keplet(ws.cell(row=r, column=7), f"=IF(A{r}=\"\",\"\",'Feladatok'!D{5 + k})", "0")
        keplet(ws.cell(row=r, column=8), f'=IF(OR(A{r}="",COUNT({T})=0),"",GEOMEAN({T}))', "0")
        keplet(ws.cell(row=r, column=9), f'=IF(OR(A{r}="",B{r}=0,G{r}=""),"",COUNTIFS({S},1,{T},"<="&G{r})/B{r})', "0%")
    rt = h0 + NF + 1
    szoveg(ws.cell(row=rt, column=1), "Összes feladat", felkov=True)
    keplet(ws.cell(row=rt, column=2), f"=SUM(B{h0 + 1}:B{rt - 1})", "0", felkov=True)
    keplet(ws.cell(row=rt, column=3), f"=SUM(C{h0 + 1}:C{rt - 1})", "0", felkov=True)
    keplet(ws.cell(row=rt, column=4), f'=IF(B{rt}=0,"",C{rt}/B{rt})', "0%", felkov=True)

    s0 = rt + 2
    szoveg(ws.cell(row=s0, column=1), "Elégedettség (SUS)", felkov=True)
    SUS = f"'Résztvevők'!D5:D{R_UT}"
    sus = [("Kitöltők száma", f"=COUNT({SUS})", "0"),
           ("SUS átlaga", f'=IF(B{s0 + 1}=0,"",AVERAGE({SUS}))', "0.0"),
           ("Szórás", f'=IF(B{s0 + 1}<2,"",STDEV({SUS}))', "0.0"),
           ("Alsó határ (t)", f'=IF(B{s0 + 1}<2,"",B{s0 + 2}-TINV(1-$B$4,B{s0 + 1}-1)*B{s0 + 3}/SQRT(B{s0 + 1}))', "0.0"),
           ("Felső határ (t)", f'=IF(B{s0 + 1}<2,"",B{s0 + 2}+TINV(1-$B$4,B{s0 + 1}-1)*B{s0 + 3}/SQRT(B{s0 + 1}))', "0.0"),
           ("Viszonyítás: a SUS-pontszámok átlaga nagy adatbázisokban", "68", None)]
    for i, (n, f, fmt) in enumerate(sus):
        szoveg(ws.cell(row=s0 + 1 + i, column=1), n)
        keplet(ws.cell(row=s0 + 1 + i, column=2), f if f != "68" else 68, fmt, felkov=(i == 1))

    p0 = s0 + 9
    szoveg(ws.cell(row=p0, column=1), "Problémafeltárás", felkov=True)
    PR = f"'Problémák'!A5:A{U_UT}"
    PE = f"'Problémák'!{EL}5:{EL}{U_UT}"
    prob = [("Feltárt problémák száma", f"=COUNTA({PR})", "0"),
            ("Ebből kritikus vagy súlyos", f"=COUNTIF('Problémák'!D5:D{U_UT},\"kritikus\")+COUNTIF('Problémák'!D5:D{U_UT},\"súlyos\")", "0"),
            ("Csak egy résztvevőnél jelentkezett", f"=COUNTIF({PE},1)", "0"),
            ("Az észlelés átlagos valószínűsége (p)", f'=IF(OR(B{p0 + 1}=0,B5=0),"",SUM({PE})/(B{p0 + 1}*B5))', "0.000"),
            ("Becsült feltárt hányad ennyi résztvevővel: 1 − (1 − p)^n", f'=IF(B{p0 + 4}="","",1-(1-B{p0 + 4})^B5)', "0%"),
            ("Becsült feltárt hányad öt résztvevővel", f'=IF(B{p0 + 4}="","",1-(1-B{p0 + 4})^5)', "0%")]
    for i, (n, f, fmt) in enumerate(prob):
        szoveg(ws.cell(row=p0 + 1 + i, column=1), n)
        keplet(ws.cell(row=p0 + 1 + i, column=2), f, fmt, felkov=(i == 4))
    megjegyzes(ws.cell(row=p0 + 4, column=1), "Kis mintán a p becslése felfelé torzít (Sauro és Lewis, 2016); a sok, csak egyszer "
                                              "észlelt probléma arra utal, hogy még vannak fel nem tárt problémák.")

    ch = BarChart()
    ch.type = "col"
    diagram_kozos(ch, "Sikerarány feladatonként", None, "sikerarány", szel=17, mag=8)
    ch.add_data(Reference(ws, min_col=4, min_row=h0, max_row=h0 + len(FELADATOK)), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=h0 + 1, max_row=h0 + len(FELADATOK)))
    ch.y_axis.scaling.min, ch.y_axis.scaling.max = 0, 1
    ch.y_axis.numFmt = "0%"
    ch.legend = None
    ws.add_chart(ch, "K4")
    return mentes(wb, "hasznalhatosagi_teszt_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
