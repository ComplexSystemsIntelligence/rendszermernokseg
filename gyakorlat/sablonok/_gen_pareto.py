"""Pareto-diagram és rétegzés (eszközlap: Pareto-diagram)."""
from openpyxl.formatting.rule import FormulaRule

from _allasido_adat import ADAT, GEPEK, OKOK
from _kozos import *  # noqa: F401,F403

NN, NO, NG = 400, 15, 10


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Pareto-diagram és rétegzés – sablon", [
        "■ Mire való? A problémák vagy okok rangsorolása gyakoriság, időtartam vagy költség szerint; a „kevés lényeges” ok kiválasztása, "
        "és az adatok rétegzése (például gépek szerint) a különbségek feltárására.",
        "■ Napló: legfeljebb 400 esemény (ellenőrzőlap): dátum, gép vagy más rétegző jellemző, ok (a listából), mérték (perc, darab, Ft).",
        "■ Okok: legfeljebb 15 ok. A Súly oszlop opcionális (például Ft/perc): ha kitöltöd, a Pareto-diagram a súlyozott hatás szerint "
        "rangsorol; üresen hagyva a súly 1. A rangsor automatikus.",
        "■ Pareto: a rangsorolt okok, arányok, kumulált arány és a diagram. Az A jelű okok együtt adják a hatás legalább 80%-át "
        "(az az ok is A, amelyik a 80%-ot átlépi).",
        "■ Rétegzés: a hatás gépenként és okonként (SUMIFS); legfeljebb 10 réteg.",
        "A kitöltött példa a ForgácsTech egy havi állásidő-naplója a MES bevezetése után (kézikönyv 25. fejezet).",
        "Források: Ishikawa: Guide to Quality Control (1982); Montgomery: Introduction to Statistical Quality Control (2020); "
        "NASA RP-1358 (1994), 5.5. és 5.6. szakasz.",
    ])

    # ---- Napló
    ws = wb.create_sheet("Napló")
    cimsor(ws, "Napló (ellenőrzőlap)", "Egy sor egy esemény. Az okot a listából válaszd.")
    ut = tablazat(ws, 4, ["Dátum", "Gép (réteg)", "Ok", "Perc"], [12, 12, 28, 9], [list(r) for r in ADAT],
                  bemeneti_oszlopok=(1, 2, 3, 4), uressor=NN - len(ADAT), formatumok={4: "0"})
    from openpyxl.worksheet.datavalidation import DataValidation
    dv = DataValidation(type="list", formula1="=Okok!$A$5:$A$19", allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"C5:C{ut}")
    ws.freeze_panes = "A5"
    N_UT = ut
    NC, NP, NGp = f"'Napló'!$C$5:$C${N_UT}", f"'Napló'!$D$5:$D${N_UT}", f"'Napló'!$B$5:$B${N_UT}"

    # ---- Okok
    ws = wb.create_sheet("Okok")
    cimsor(ws, "Okok", "A rangsor a súlyozott hatás szerint automatikus.")
    fej = ["Ok", "Súly (például Ft/perc)", "Események", "Perc", "Hatás", "Rendezési kulcs", "Rang"]
    sorok = [[ok, None] for ok in OKOK]
    ut = tablazat(ws, 4, fej, [28, 14, 11, 10, 11, 14, 8], sorok, bemeneti_oszlopok=(1, 2),
                  kepletek={3: lambda r: f'=IF(A{r}="","",COUNTIF({NC},A{r}))',
                            4: lambda r: f'=IF(A{r}="","",SUMIF({NC},A{r},{NP}))',
                            5: lambda r: f'=IF(A{r}="","",D{r}*IF(B{r}="",1,B{r}))',
                            6: lambda r: f'=IF(A{r}="",-1,E{r}+(1000-ROW())/1000000000)',
                            7: lambda r: f'=IF(A{r}="","",COUNTIF($F$5:$F${4 + NO},">"&F{r})+1)'},
                  uressor=NO - len(OKOK), formatumok={3: "0", 4: "0", 5: "#,##0", 6: "0.000", 7: "0"})
    szoveg(ws.cell(row=ut + 1, column=1), "Összesen", felkov=True)
    keplet(ws.cell(row=ut + 1, column=3), f"=SUM(C5:C{ut})", "0", True)
    keplet(ws.cell(row=ut + 1, column=4), f"=SUM(D5:D{ut})", "0", True)
    keplet(ws.cell(row=ut + 1, column=5), f"=SUM(E5:E{ut})", "#,##0", True)
    szoveg(ws.cell(row=ut + 2, column=1), "A naplóban szereplő, de a listában nem található okok eseményei")
    keplet(ws.cell(row=ut + 2, column=3), f"=COUNTA({NC})-C{ut + 1}", "0", True)
    ws.conditional_formatting.add(f"C{ut + 2}", FormulaRule(formula=[f"C{ut + 2}>0"], fill=PatternFill("solid", fgColor="F6D5D5")))
    O = lambda c: f"'Okok'!${c}$5:${c}${4 + NO}"

    # ---- Pareto
    ws = wb.create_sheet("Pareto")
    cimsor(ws, "Pareto-diagram", "A okok: a hatás legalább 80%-át adják együtt.")
    fej = ["Rang", "Ok", "Hatás", "Arány", "Kumulált arány", "Osztály"]
    fejlec(ws, 4, fej, [7, 30, 11, 10, 14, 9])
    for k in range(NO):
        r = 5 + k
        szoveg(ws.cell(row=r, column=1), k + 1)
        keplet(ws.cell(row=r, column=2), f'=IFERROR(INDEX({O("A")},MATCH(A{r},{O("G")},0)),"")')
        keplet(ws.cell(row=r, column=3), f'=IF(B{r}="","",INDEX({O("E")},MATCH(A{r},{O("G")},0)))', "#,##0")
        keplet(ws.cell(row=r, column=4), f'=IF(B{r}="","",C{r}/SUM($C$5:$C${4 + NO}))', "0.0%")
        keplet(ws.cell(row=r, column=5), f'=IF(B{r}="","",SUM($D$5:D{r}))', "0.0%")
        keplet(ws.cell(row=r, column=6), f'=IF(B{r}="","",IF(E{r}-D{r}<0.8-0.000001,"A","B"))', None, True)
    ws.conditional_formatting.add(f"F5:F{4 + NO}", FormulaRule(formula=['F5="A"'], fill=PatternFill("solid", fgColor="F4D9A8")))
    ch = BarChart()
    ch.add_data(Reference(ws, min_col=3, min_row=4, max_row=4 + len(OKOK)), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=2, min_row=5, max_row=4 + len(OKOK)))
    diagram_kozos(ch, "Pareto-diagram", None, "hatás", 22, 10)
    lc = LineChart()
    lc.add_data(Reference(ws, min_col=5, min_row=4, max_row=4 + len(OKOK)), titles_from_data=True)
    lc.y_axis.axId = 200
    lc.y_axis.number_format = "0%"
    lc.y_axis.scaling.min, lc.y_axis.scaling.max = 0, 1
    lc.y_axis.crosses = "max"
    lc.y_axis.delete = False
    ch += lc
    ws.add_chart(ch, "H4")

    # ---- Rétegzés
    ws = wb.create_sheet("Rétegzés")
    cimsor(ws, "Rétegzés: hatás rétegenként és okonként", "A rétegeket (például gépeket) a B4:K4 cellákba írd.")
    c = ws.cell(row=4, column=1, value="Ok \\ réteg")
    c.font, c.fill, c.alignment, c.border = fej_font, fej_fill, kozep, keret
    ws.column_dimensions["A"].width = 28
    for j in range(NG):
        bemenet(ws.cell(row=4, column=2 + j), GEPEK[j] if j < len(GEPEK) else None)
        ws.column_dimensions[get_column_letter(2 + j)].width = 9
    c = ws.cell(row=4, column=2 + NG, value="Összesen")
    c.font, c.fill, c.alignment, c.border = fej_font, fej_fill, kozep, keret
    for i in range(NO):
        r = 5 + i
        keplet(ws.cell(row=r, column=1), f"=IF('Okok'!A{5 + i}=\"\",\"\",'Okok'!A{5 + i})")
        for j in range(NG):
            cl = get_column_letter(2 + j)
            keplet(ws.cell(row=r, column=2 + j),
                   f'=IF(OR($A{r}="",{cl}$4=""),"",SUMIFS({NP},{NC},$A{r},{NGp},{cl}$4))', "0")
        keplet(ws.cell(row=r, column=2 + NG), f'=IF($A{r}="","",SUM(B{r}:{get_column_letter(1 + NG)}{r}))', "0", True)
    rt = 5 + NO
    szoveg(ws.cell(row=rt, column=1), "Összesen", felkov=True)
    for j in range(NG + 1):
        cl = get_column_letter(2 + j)
        keplet(ws.cell(row=rt, column=2 + j), f'=IF({cl}$4="","",SUM({cl}5:{cl}{rt - 1}))' if j < NG else f"=SUM({cl}5:{cl}{rt - 1})", "0", True)
    ch = BarChart()
    ch.type, ch.grouping, ch.overlap = "col", "stacked", 100
    diagram_kozos(ch, "Hatás rétegenként, okok szerint", None, "perc", 22, 10)
    ch.add_data(Reference(ws, min_col=1, max_col=1 + len(GEPEK), min_row=5, max_row=4 + len(OKOK)), from_rows=True, titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=2, max_col=1 + len(GEPEK), min_row=4))
    ws.add_chart(ch, "A23")
    return mentes(wb, "pareto_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
