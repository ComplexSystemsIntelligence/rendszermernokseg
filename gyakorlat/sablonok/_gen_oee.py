"""OEE-számítás (eszközlap: OEE-számítás)."""
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties

from _kozos import *  # noqa: F401,F403

# műszak, tervezett idő, átállások száma, átállás [perc], meghibásodás [perc], kisebb leállások [perc], legyártott, jó, indítási selejt
MUSZAKOK = [
    (1, 450, 2, 93, 55, 26, 62, 59, 3), (2, 450, 2, 91, 0, 20, 76, 72, 2), (3, 450, 1, 51, 0, 25, 84, 79, 1),
    (4, 450, 2, 95, 0, 28, 73, 69, 1), (5, 450, 2, 103, 30, 21, 66, 62, 0), (6, 450, 2, 78, 69, 17, 64, 63, 0),
    (7, 450, 2, 112, 0, 24, 70, 68, 0), (8, 450, 2, 95, 0, 23, 74, 69, 3), (9, 450, 2, 103, 0, 29, 71, 64, 1),
    (10, 450, 1, 47, 0, 14, 87, 81, 0), (11, 450, 2, 92, 103, 18, 53, 49, 3), (12, 450, 2, 101, 0, 17, 74, 71, 1),
    (13, 450, 2, 104, 0, 12, 75, 73, 0), (14, 450, 2, 94, 25, 23, 69, 64, 2), (15, 450, 2, 94, 75, 25, 57, 53, 4),
    (16, 450, 3, 154, 43, 18, 52, 52, 0), (17, 450, 2, 87, 0, 30, 74, 68, 3), (18, 450, 3, 121, 0, 27, 67, 64, 1),
    (19, 450, 2, 100, 0, 26, 72, 63, 4), (20, 450, 2, 105, 0, 17, 80, 77, 1),
]
N = 40
OLE = [("1. szerelő", 450, 45, 340, 20, 19), ("2. szerelő", 450, 30, 372, 22, 22), ("3. szerelő", 450, 60, 318, 18, 16)]


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "OEE-számítás – sablon", [
        "■ Mire való? Egy berendezés teljes eszközhatékonyságának (OEE) számítása műszakonkénti adatokból: rendelkezésre állás (A), teljesítmény (P), minőség (Q), a hat nagy veszteség percben, OEE-vízesés, a beállításiidő-csökkentés (SMED) hatása, valamint a munkaerő-hatékonyság (OLE) (kézikönyv 19. fejezet; Nakajima, 1988; Muchiri és Pintelon, 2008).",
        "1. Az „Adatok” lapon add meg a gép nevét és az ideális ciklusidőt (perc/db). Több termék esetén az ideális ciklusidő a termékösszetétellel súlyozott egyenérték, vagy a P tényezőt termékenként kell számolni.",
        "2. Soronként egy műszak (vagy nap): tervezett üzemidő (a műszakidő a tervezett szünetek nélkül), átállások száma és ideje, meghibásodások ideje, a rögzített kisebb leállások ideje, a legyártott, a jó és az indításkor selejtté vált darabok száma.",
        "3. A sablon kiszámítja a működési időt, az A, P, Q tényezőt és az OEE-t műszakonként, valamint az időszakra. Az időszaki értéket az összegekből számolja, nem a műszakonkénti arányok átlagából.",
        "4. A „Veszteségek” lap a hat nagy veszteséget percben és arányban mutatja, és megrajzolja az egy műszakra jutó OEE-vízesést. A csökkentett sebesség a működési idő, a kisebb leállások és az ideális gyártási idő különbsége.",
        "5. A „SMED” lap azt mutatja, hogyan változik a rendelkezésre állás és az OEE, ha az átállás rövidebb, és ha a megtakarítást több átállásra (kisebb sorozatokra) fordítjuk.",
        "6. Az „OLE” lap a munkaerő rendelkezésre állását, teljesítményét és minőségét összesíti.",
        "■ Az OEE egy gép mutatója: a saját korábbi értékeihez érdemes hasonlítani, nem más gépekhez vagy üzemekhez. A kézzel rögzített kisebb leállások gyakran hiányosak; ha lehet, gépi adatgyűjtést használj.",
        "■ Példa: a ForgácsTech megmunkáló központja, 20 műszak (kézikönyv 19. fejezet). Az OLE-példa a VárosiBringa javítóműhelye.",
    ])
    ws = wb.create_sheet("Adatok")
    cimsor(ws, "Műszakonkénti adatok")
    szoveg(ws["A3"], "Berendezés", felkov=True); bemenet(ws["B3"], "többtengelyes megmunkáló központ")
    szoveg(ws["A4"], "Ideális ciklusidő [perc/db]", felkov=True); bemenet(ws["B4"], 4, "0.00")
    ws.merge_cells("B3:D3")
    fej = ["Műszak", "Tervezett üzemidő [perc]", "Átállások száma", "Átállás [perc]", "Meghibásodás [perc]", "Kisebb leállások [perc]",
           "Legyártott [db]", "Jó [db]", "Indítási selejt [db]", "Működési idő [perc]", "A", "Ideális gyártási idő [perc]", "P", "Q", "OEE",
           "Csökkentett sebesség [perc]", "Folyamatselejt [db]"]
    r1, rn = 8, 7 + N
    kepl = {10: lambda r: f'=IF(OR(A{r}="",B{r}=""),"",B{r}-D{r}-E{r})',
            11: lambda r: f'=IF(J{r}="","",J{r}/B{r})',
            12: lambda r: f'=IF(J{r}="","",G{r}*$B$4)',
            13: lambda r: f'=IF(OR(J{r}="",N(J{r})=0),"",L{r}/J{r})',
            14: lambda r: f'=IF(OR(J{r}="",N(G{r})=0),"",H{r}/G{r})',
            15: lambda r: f'=IF(OR(K{r}="",M{r}="",N{r}=""),"",K{r}*M{r}*N{r})',
            16: lambda r: f'=IF(J{r}="","",J{r}-F{r}-L{r})',
            17: lambda r: f'=IF(J{r}="","",G{r}-H{r}-I{r})'}
    tablazat(ws, 7, fej, [9, 12, 10, 10, 12, 12, 11, 9, 10, 11, 8, 12, 8, 8, 8, 12, 11], [list(m) for m in MUSZAKOK],
             bemeneti_oszlopok=tuple(range(1, 10)), kepletek=kepl, uressor=N - len(MUSZAKOK),
             formatumok={11: "0.0%", 13: "0.0%", 14: "0.0%", 15: "0.0%", 10: "0", 12: "0", 16: "0"})
    ro = rn + 1
    szoveg(ws.cell(row=ro, column=1), "Összesen", felkov=True)
    for col in "BCDEFGHIJLPQ":
        keplet(ws[f"{col}{ro}"], f"=SUM({col}{r1}:{col}{rn})", "0", True)
    keplet(ws[f"K{ro}"], f'=IF(B{ro}=0,"",J{ro}/B{ro})', "0.0%", True)
    keplet(ws[f"M{ro}"], f'=IF(J{ro}=0,"",L{ro}/J{ro})', "0.0%", True)
    keplet(ws[f"N{ro}"], f'=IF(G{ro}=0,"",H{ro}/G{ro})', "0.0%", True)
    keplet(ws[f"O{ro}"], f'=IF(B{ro}=0,"",K{ro}*M{ro}*N{ro})', "0.0%", True)
    szoveg(ws.cell(row=ro + 1, column=1), "Műszakok száma", felkov=True)
    keplet(ws.cell(row=ro + 1, column=2), f'=COUNT(B{r1}:B{rn})', "0", True)
    szoveg(ws.cell(row=ro + 2, column=1), "Ellenőrzés", felkov=True)
    keplet(ws.cell(row=ro + 2, column=2), f'=IF(COUNTIF(P{r1}:P{rn},"<0")+COUNTIF(Q{r1}:Q{rn},"<0")>0,"HIBA: negatív sebesség- vagy selejtveszteség – ellenőrizd az adatokat","rendben")', None, True)
    ws.merge_cells(start_row=ro + 2, start_column=2, end_row=ro + 2, end_column=8)
    ch = LineChart()
    ch.add_data(Reference(ws, min_col=11, max_col=11, min_row=7, max_row=7 + len(MUSZAKOK)), titles_from_data=True)
    for col in (13, 14, 15):
        ch.add_data(Reference(ws, min_col=col, max_col=col, min_row=7, max_row=7 + len(MUSZAKOK)), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=8, max_row=7 + len(MUSZAKOK)))
    diagram_kozos(ch, "A, P, Q és OEE műszakonként", "műszak", None, 22, 9)
    ch.y_axis.number_format = "0%"
    ws.add_chart(ch, f"S7")
    D = "Adatok!"

    v = wb.create_sheet("Veszteségek")
    cimsor(v, "A hat nagy veszteség és az OEE-vízesés")
    fejlec(v, 3, ["Veszteség", "Csoport", "Időszak [perc]", "Egy műszakra [perc]", "Arány a tervezett időhöz"], [34, 16, 14, 14, 14])
    tv = f"{D}$B${ro}"
    ms = f"{D}$B${ro + 1}"
    vesz = [("1. meghibásodás", "állásidő", f"={D}E{ro}"), ("2. beállítás, átállás", "állásidő", f"={D}D{ro}"),
            ("3. üresjárat, kisebb leállások", "sebesség", f"={D}F{ro}"), ("4. csökkentett sebesség", "sebesség", f"={D}P{ro}"),
            ("5. selejt és utómunka", "minőség", f"={D}Q{ro}*{D}$B$4"), ("6. indítási veszteség", "minőség", f"={D}I{ro}*{D}$B$4")]
    for i, (n_, g, f) in enumerate(vesz):
        r = 4 + i
        szoveg(v.cell(row=r, column=1), n_); szoveg(v.cell(row=r, column=2), g)
        keplet(v.cell(row=r, column=3), f, "0")
        keplet(v.cell(row=r, column=4), f'=IF({ms}=0,"",C{r}/{ms})', "0.0")
        keplet(v.cell(row=r, column=5), f'=IF({tv}=0,"",C{r}/{tv})', "0.0%")
    szoveg(v["A10"], "Értékes idő (jó darabok ideális ideje)", felkov=True)
    keplet(v["C10"], f"={D}H{ro}*{D}$B$4", "0", True)
    keplet(v["D10"], f'=IF({ms}=0,"",C10/{ms})', "0.0", True)
    keplet(v["E10"], f'=IF({tv}=0,"",C10/{tv})', "0.0%", True)
    szoveg(v["A11"], "Ellenőrzés: veszteségek + értékes idő = tervezett idő", felkov=True)
    keplet(v["C11"], f'=IF(ABS(SUM(C4:C10)-{tv})<0.5,"rendben","eltérés")', None, True)
    bc = BarChart(); bc.type = "bar"
    bc.add_data(Reference(v, min_col=4, min_row=3, max_row=9), titles_from_data=True)
    bc.set_categories(Reference(v, min_col=1, min_row=4, max_row=9))
    bc.x_axis.scaling.orientation = "maxMin"
    diagram_kozos(bc, "A hat nagy veszteség egy műszakra [perc]", None, "perc", 16, 8)
    bc.legend = None
    v.add_chart(bc, "G3")
    # vízesés: láthatatlan alap + látható érték
    fejlec(v, 14, ["Lépcső", "Alap", "Érték"], [34, 16, 14])
    lepcs = [("tervezett üzemidő", "=0", "=SUM(C4:C10)/" + ms),
             ("− átállás", "=C15-C16-D5", "=D5"),
             ("− meghibásodás", "=B16-D4", "=D4"),
             ("működési idő", "=0", "=C15-D4-D5"),
             ("− sebességveszteség", "=C18-D6-D7", "=D6+D7"),
             ("nettó működési idő", "=0", "=C18-D6-D7"),
             ("− minőségi veszteség", "=C20-D8-D9", "=D8+D9"),
             ("értékes idő", "=0", "=D10")]
    for i, (n_, b, c_) in enumerate(lepcs):
        r = 15 + i
        szoveg(v.cell(row=r, column=1), n_)
        keplet(v.cell(row=r, column=2), b, "0.0")
        keplet(v.cell(row=r, column=3), c_, "0.0")
    # a 16. sor alapja: tervezett − átállás (a sáv a tervezett idő tetejéről lóg le)
    v["B16"] = "=C15-D5"
    v["B17"] = "=C15-D5-D4"
    wf = BarChart(); wf.grouping = "stacked"; wf.overlap = 100
    wf.add_data(Reference(v, min_col=2, max_col=3, min_row=14, max_row=22), titles_from_data=True)
    wf.set_categories(Reference(v, min_col=1, min_row=15, max_row=22))
    wf.series[0].graphicalProperties = GraphicalProperties(noFill=True, ln=LineProperties(noFill=True))
    diagram_kozos(wf, "OEE-vízesés egy műszakra [perc]", None, "perc", 20, 9)
    wf.legend = None
    v.add_chart(wf, "G20")

    s = wb.create_sheet("SMED")
    cimsor(s, "A beállítási idő csökkentésének hatása")
    alap = [("Tervezett üzemidő műszakonként [perc]", f"={D}B{ro}/{D}B{ro + 1}", "0"),
            ("Meghibásodás műszakonként [perc]", f"={D}E{ro}/{D}B{ro + 1}", "0.0"),
            ("Teljesítménytényező P (az adatokból)", f"={D}M{ro}", "0.0%"),
            ("Minőségi tényező Q (az adatokból)", f"={D}N{ro}", "0.0%"),
            ("Jelenlegi átállások száma műszakonként", f"={D}C{ro}/{D}B{ro + 1}", "0.0"),
            ("Jelenlegi átlagos átállási idő [perc]", f'=IF({D}C{ro}=0,"",{D}D{ro}/{D}C{ro})', "0.0")]
    for i, (t, f, fmt) in enumerate(alap):
        szoveg(s.cell(row=3 + i, column=1), t)
        keplet(s.cell(row=3 + i, column=2), f, fmt, True)
    fejlec(s, 10, ["Változat", "Átállások száma műszakonként", "Átállási idő [perc]", "Átállás műszakonként [perc]", "A", "OEE",
                   "Sorozatnagyság a jelenlegihez képest", "Gép előtti készlet a jelenlegihez képest"], [36, 14, 12, 14, 9, 9, 16, 16])
    valt = [("jelenlegi", "=B7", "=B8"), ("SMED, azonos sorozatnagyság", 2, 8), ("SMED, fele akkora sorozatok", 4, 8),
            ("SMED, negyed akkora sorozatok", 8, 8)]
    for i, (n_, c_, t_) in enumerate(valt):
        r = 11 + i
        bemenet(s.cell(row=r, column=1), n_)
        if isinstance(c_, str):
            keplet(s.cell(row=r, column=2), c_, "0.0"); keplet(s.cell(row=r, column=3), t_, "0.0")
        else:
            bemenet(s.cell(row=r, column=2), c_, "0.0"); bemenet(s.cell(row=r, column=3), t_, "0.0")
        keplet(s.cell(row=r, column=4), f"=B{r}*C{r}", "0")
        keplet(s.cell(row=r, column=5), f'=IF($B$3=0,"",($B$3-D{r}-$B$4)/$B$3)', "0.0%")
        keplet(s.cell(row=r, column=6), f'=IF(E{r}="","",E{r}*$B$5*$B$6)', "0.0%", True)
        keplet(s.cell(row=r, column=7), f'=IF(B{r}=0,"",$B$11/B{r})', "0.00")
        keplet(s.cell(row=r, column=8), f'=IF(B{r}=0,"",$B$11/B{r})', "0.00")
    szoveg(s["A16"], "Feltevés: a sorozatnagyság fordítottan arányos az átállások számával, és a gép előtti készlet a sorozatnagysággal arányos; a Little-törvény szerint a gép előtti várakozási idő is ezzel arányosan változik (változatlan áram mellett). A P és Q tényezőt változatlannak tekintjük.")
    s.merge_cells("A16:H17")
    s.row_dimensions[16].height = 30

    o = wb.create_sheet("OLE")
    cimsor(o, "Teljes munkaerő-hatékonyság (OLE)")
    fej = ["Dolgozó", "Tervezett munkaidő [perc]", "Nem rendelkezésre álló idő [perc] (várakozás, megbeszélés, hiány)",
           "Elvégzett munkák normaideje [perc]", "Elvégzett munkák [db]", "Elsőre jó munkák [db]", "A", "P", "Q", "OLE"]
    kepl = {7: lambda r: f'=IF(OR(A{r}="",N(B{r})=0),"",(B{r}-C{r})/B{r})',
            8: lambda r: f'=IF(OR(A{r}="",B{r}-C{r}<=0),"",D{r}/(B{r}-C{r}))',
            9: lambda r: f'=IF(OR(A{r}="",N(E{r})=0),"",F{r}/E{r})',
            10: lambda r: f'=IF(OR(G{r}="",H{r}="",I{r}=""),"",G{r}*H{r}*I{r})'}
    u = tablazat(o, 3, fej, [16, 12, 22, 14, 11, 11, 8, 8, 8, 8], [list(x) for x in OLE], bemeneti_oszlopok=(1, 2, 3, 4, 5, 6),
                 kepletek=kepl, uressor=7, formatumok={7: "0.0%", 8: "0.0%", 9: "0.0%", 10: "0.0%"})
    ru = u + 1
    szoveg(o.cell(row=ru, column=1), "Összesen", felkov=True)
    for col in "BCDEF":
        keplet(o[f"{col}{ru}"], f"=SUM({col}4:{col}{u})", "0", True)
    keplet(o[f"G{ru}"], f'=IF(B{ru}=0,"",(B{ru}-C{ru})/B{ru})', "0.0%", True)
    keplet(o[f"H{ru}"], f'=IF(B{ru}-C{ru}<=0,"",D{ru}/(B{ru}-C{ru}))', "0.0%", True)
    keplet(o[f"I{ru}"], f'=IF(E{ru}=0,"",F{ru}/E{ru})', "0.0%", True)
    keplet(o[f"J{ru}"], f'=IF(G{ru}="","",G{ru}*H{ru}*I{ru})', "0.0%", True)
    szoveg(o.cell(row=ru + 2, column=1), "Az OLE célja a munkaszervezési veszteségek (várakozás, hiány, utómunka) feltárása, nem a dolgozók rangsorolása.")
    return mentes(wb, "oee_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
