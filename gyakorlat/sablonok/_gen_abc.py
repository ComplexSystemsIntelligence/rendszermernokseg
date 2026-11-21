"""ABC-elemzés és készlethatékonyság (eszközlap: ABC-elemzés és készlethatékonyság)."""
from openpyxl.chart import BarChart, LineChart, Reference

from _abc_adat import ADAT
from _kozos import *  # noqa: F401,F403

N = 60
HONAPOK = ["jan.", "febr.", "márc.", "ápr.", "máj.", "jún.", "júl.", "aug.", "szept.", "okt.", "nov.", "dec."]
KESZLET = [29.8, 32.4, 33.1, 31.0, 30.2, 29.5, 31.8, 32.6, 30.9, 30.4, 31.5, 29.6]   # MFt, hó végi készletérték


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "ABC-elemzés és készlethatékonyság – sablon", [
        "■ Mire való? Készlettételek csoportosítása éves felhasználási értékük (ABC) és felhasználásuk ingadozása (XYZ) szerint, a differenciált készletgazdálkodás megtervezéséhez; a készletforgás és a készlethatékonyság számítása (kézikönyv 21. fejezet; Silver és mtsai, 2016).",
        "1. A „Tételek” lapon soronként egy tétel: cikkszám, megnevezés, egységár (Ft), és a 12 havi felhasználás mennyiségben. Ha csak éves adatod van, írd az éves mennyiséget a januári oszlopba, és az XYZ-oszlopokat hagyd figyelmen kívül.",
        "2. A sablon kiszámítja az éves mennyiséget és értéket, a havi felhasználás relatív szórását (CV), a tétel érték szerinti rangját, és a „Pareto” lapon a kumulált érték- és tételarányokat.",
        "3. Az ABC-besorolás alapja választható: tételszám szerint (alapértelmezés: az első 20% A, a következő 40% B, a többi C) vagy érték szerint (a kumulált érték 80%-áig A, 95%-áig B). A határok a „Pareto” lap tetején módosíthatók.",
        "4. Az XYZ-besorolás a havi felhasználás relatív szórása szerint: X (egyenletes) legfeljebb 0,5, Y legfeljebb 1,0, Z (szórványos) felette; a határok módosíthatók.",
        "5. Az „Összesítés” lap csoportonként mutatja a tételszámot és az értéket, valamint az ABC–XYZ mátrixot a javasolt szabályozással.",
        "6. A „Készlethatékonyság” lap a havi készletértékekből és az éves felhasználásból számítja az átlagos készletet, a fordulatszámot, a készletnapokat és az 1000 Ft forgalomra jutó készletet.",
        "■ Példa: a ForgácsTech anyag- és szerszámtételei (kézikönyv 21. fejezet).",
    ])
    t = wb.create_sheet("Tételek")
    cimsor(t, "Tételek és havi felhasználás")
    r1, rn = 4, 3 + N
    fej = ["Cikkszám", "Megnevezés", "Egységár [Ft]"] + HONAPOK + ["Éves mennyiség", "Éves érték [eFt]", "Havi átlag", "Havi szórás", "CV", "Érték szerinti rang", "ABC", "XYZ", "Csoport"]
    c_ev, c_ert = 16, 17
    kepl = {16: lambda r: f'=IF(A{r}="","",SUM(D{r}:O{r}))',
            17: lambda r: f'=IF(A{r}="","",P{r}*C{r}/1000)',
            18: lambda r: f'=IF(A{r}="","",AVERAGE(D{r}:O{r}))',
            19: lambda r: f'=IF(OR(A{r}="",COUNT(D{r}:O{r})<2),"",STDEV(D{r}:O{r}))',
            20: lambda r: f'=IF(OR(S{r}="",N(R{r})=0),"",S{r}/R{r})',
            21: lambda r: f'=IF(A{r}="","",COUNTIF($Q${r1}:$Q${rn},">"&Q{r})+COUNTIF($Q${r1}:Q{r},Q{r}))',
            22: lambda r: f'=IF(A{r}="","",INDEX(Pareto!$H$9:$H${8 + N},U{r}))',
            23: lambda r: f'=IF(OR(A{r}="",T{r}=""),"",IF(T{r}<=Pareto!$B$5,"X",IF(T{r}<=Pareto!$B$6,"Y","Z")))',
            24: lambda r: f'=IF(A{r}="","",V{r}&W{r})'}
    tablazat(t, 3, fej, [13, 30, 11] + [7] * 12 + [11, 12, 10, 10, 7, 9, 6, 6, 8], [[a, b, c] + d for a, b, c, d in ADAT],
             bemeneti_oszlopok=tuple(range(1, 16)), kepletek=kepl, uressor=N - len(ADAT),
             formatumok={3: "#,##0", 16: "#,##0", 17: "#,##0.0", 18: "#,##0.0", 19: "#,##0.0", 20: "0.00", **{c: "#,##0" for c in range(4, 16)}})

    p = wb.create_sheet("Pareto")
    cimsor(p, "Pareto-sorrend és ABC-besorolás")
    szoveg(p["A3"], "Az ABC-besorolás alapja", felkov=True); bemenet(p["B3"], "tételszám"); legordulo(p, "B3", ["tételszám", "érték"])
    szoveg(p["D3"], "A-határ", felkov=True); szoveg(p["D4"], "B-határ (kumulált)", felkov=True)
    szoveg(p["E2"], "tételszám", felkov=True); szoveg(p["F2"], "érték", felkov=True)
    bemenet(p["E3"], 0.20, "0%"); bemenet(p["E4"], 0.60, "0%"); bemenet(p["F3"], 0.80, "0%"); bemenet(p["F4"], 0.95, "0%")
    szoveg(p["A5"], "X-határ (CV)", felkov=True); bemenet(p["B5"], 0.5, "0.00")
    szoveg(p["A6"], "Y-határ (CV)", felkov=True); bemenet(p["B6"], 1.0, "0.00")
    fej = ["Hely", "Cikkszám", "Megnevezés", "Éves érték [eFt]", "Kumulált érték [eFt]", "Kumulált értékarány", "Kumulált tételarány", "ABC"]
    fejlec(p, 8, fej, [8, 13, 30, 13, 14, 13, 13, 7])
    T = lambda c: f"Tételek!${c}${r1}:${c}${rn}"
    db = f'COUNT({T("Q")})'
    for k in range(N):
        r = 9 + k
        szoveg(p.cell(row=r, column=1), k + 1)
        keplet(p.cell(row=r, column=2), f'=IFERROR(INDEX({T("A")},MATCH(A{r},{T("U")},0)),"")')
        keplet(p.cell(row=r, column=3), f'=IF(B{r}="","",INDEX({T("B")},MATCH(A{r},{T("U")},0)))')
        keplet(p.cell(row=r, column=4), f'=IF(B{r}="","",INDEX({T("Q")},MATCH(A{r},{T("U")},0)))', "#,##0.0")
        keplet(p.cell(row=r, column=5), f'=IF(B{r}="","",SUM($D$9:D{r}))', "#,##0.0")
        keplet(p.cell(row=r, column=6), f'=IF(B{r}="","",E{r}/SUM($D$9:$D${8 + N}))', "0.0%")
        keplet(p.cell(row=r, column=7), f'=IF(B{r}="","",A{r}/{db})', "0.0%")
        # tételszám szerint: a hely aránya; érték szerint: a tétel ELŐTTI kumulált érték aránya
        elotte = f"(F{r}-D{r}/SUM($D$9:$D${8 + N}))"
        keplet(p.cell(row=r, column=8),
               f'=IF(B{r}="","",IF($B$3="érték",IF({elotte}<$F$3,"A",IF({elotte}<$F$4,"B","C")),IF(G{r}<=$E$3+0.0001,"A",IF(G{r}<=$E$4+0.0001,"B","C"))))', None, True)
    ch = BarChart()
    ch.add_data(Reference(p, min_col=4, min_row=8, max_row=8 + len(ADAT)), titles_from_data=True)
    ch.set_categories(Reference(p, min_col=2, min_row=9, max_row=8 + len(ADAT)))
    diagram_kozos(ch, "Pareto-diagram: éves érték és kumulált arány", None, "eFt", 24, 10)
    lc = LineChart()
    lc.add_data(Reference(p, min_col=6, min_row=8, max_row=8 + len(ADAT)), titles_from_data=True)
    lc.y_axis.axId = 200
    lc.y_axis.number_format = "0%"
    lc.y_axis.crosses = "max"
    lc.y_axis.delete = False
    ch += lc
    p.add_chart(ch, "J8")

    o = wb.create_sheet("Összesítés")
    cimsor(o, "Csoportonkénti összesítés és ABC–XYZ mátrix")
    fejlec(o, 3, ["Csoport", "Tételek száma", "Tételarány", "Éves érték [eFt]", "Értékarány"], [12, 13, 12, 15, 12])
    for k, g in enumerate("ABC"):
        r = 4 + k
        szoveg(o.cell(row=r, column=1), g, felkov=True)
        keplet(o.cell(row=r, column=2), f'=COUNTIF({T("V")},A{r})', "0")
        keplet(o.cell(row=r, column=3), f'=IF(SUM($B$4:$B$6)=0,"",B{r}/SUM($B$4:$B$6))', "0%")
        keplet(o.cell(row=r, column=4), f'=SUMIF({T("V")},A{r},{T("Q")})', "#,##0")
        keplet(o.cell(row=r, column=5), f'=IF(SUM($D$4:$D$6)=0,"",D{r}/SUM($D$4:$D$6))', "0%", True)
    szoveg(o["A7"], "Összesen", felkov=True)
    keplet(o["B7"], "=SUM(B4:B6)", "0", True); keplet(o["D7"], "=SUM(D4:D6)", "#,##0", True)
    fejlec(o, 9, ["Tételek száma", "X (egyenletes)", "Y (ingadozó)", "Z (szórványos)"], [16, 14, 14, 14])
    for k, g in enumerate("ABC"):
        r = 10 + k
        szoveg(o.cell(row=r, column=1), g, felkov=True)
        for j, x in enumerate("XYZ"):
            keplet(o.cell(row=r, column=2 + j), f'=COUNTIF({T("X")},"{g}{x}")', "0", True)
    fejlec(o, 14, ["Csoport", "Javasolt szabályozás (kiindulópont, a vállalati körülményekhez igazítandó)"], [12, 100])
    javas = [("AX", "pontos előrejelzés és nyilvántartás, gyakori (heti) felülvizsgálat, rendeléshez vagy ütemtervhez kötött beszerzés, kis biztonsági készlet"),
             ("AY, AZ", "egyedi tervezés: keretszerződés lehívással, biztonsági készlet az ingadozás szerint, a beszerzési idő folyamatos követése"),
             ("B", "az A-hoz hasonló, de ritkább felülvizsgálat; rendelési pont vagy periodikus rendelés"),
             ("C", "egyszerű nyilvántartás, nagyobb rendelési tételek, keretrendelés, szemrevételezéses ellenőrzés; a Z-tételeknél rendelésre beszerzés")]
    for k, (g, s) in enumerate(javas):
        szoveg(o.cell(row=15 + k, column=1), g, felkov=True)
        szoveg(o.cell(row=15 + k, column=2), s)

    k = wb.create_sheet("Készlethatékonyság")
    cimsor(k, "Készletforgás és készlethatékonyság")
    for i, (tx, v, fmt) in enumerate([("Éves felhasználás (forgalom) [MFt]", "=Tételek!Q1", "#,##0.0"), ("A naptári napok száma", 365, "0"), ("Munkanapok száma", 230, "0")]):
        szoveg(k.cell(row=3 + i, column=1), tx, felkov=True)
        if isinstance(v, str):
            keplet(k.cell(row=3 + i, column=2), f'=SUM(Tételek!$Q${r1}:$Q${rn})/1000', fmt, True)
        else:
            bemenet(k.cell(row=3 + i, column=2), v, fmt)
    fejlec(k, 7, ["Hónap", "Hó végi készletérték [MFt]"], [34, 16])
    for i, (h, v) in enumerate(zip(HONAPOK, KESZLET)):
        szoveg(k.cell(row=8 + i, column=1), h)
        bemenet(k.cell(row=8 + i, column=2), v, "0.0")
    for i, (tx, f, fmt) in enumerate([
        ("Átlagos készlet [MFt]", "=AVERAGE(B8:B19)", "0.0"),
        ("Fordulatszám [1/év] = felhasználás / átlagos készlet", '=IF(B21=0,"",B3/B21)', "0.00"),
        ("Készlet naptári napokban", '=IF(N(B22)=0,"",B4/B22)', "0.0"),
        ("Készlet munkanapokban", '=IF(N(B22)=0,"",B5/B22)', "0.0"),
        ("Készlethatékonyság: készlet 1000 Ft forgalomra [Ft]", '=IF(B3=0,"",B21/B3*1000)', "0"),
    ]):
        szoveg(k.cell(row=21 + i, column=1), tx)
        keplet(k.cell(row=21 + i, column=2), f, fmt, True)
    szoveg(k["A27"], "A készlet napokban a Little-törvény alkalmazása: átlagosan ennyi ideig marad egy anyagegység a raktárban. A forgalmat és a készletet azonos értékalapon (például bekerülési áron) kell mérni.")
    k.merge_cells("A27:F28")
    k.row_dimensions[27].height = 30
    return mentes(wb, "abc_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
