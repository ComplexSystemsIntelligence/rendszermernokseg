"""Munkalebontási struktúra, hálós ütemterv (CPM és PERT) és megszerzett érték (eszközlap: Munkalebontási struktúra)."""
from openpyxl.formatting.rule import FormulaRule

from _kozos import *  # noqa: F401,F403
from _wbs_adat import AC, BAC, CEL_HET, EV, HONAP, PV, TEV, WBS

NW, NT, NP, RACS, NH = 60, 40, 4, 40, 24


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Munkalebontási struktúra, ütemezés és megszerzett érték – sablon", [
        "■ Mire való? A projekt munkájának termékorientált, hierarchikus felosztása (WBS), a 100%-szabály ellenőrzése és a költségek "
        "összesítése; hálós ütemterv a kritikus úttal és a tartalékokkal, hárompontos (PERT) becsléssel; a megszerzett érték követése.",
        "■ WBS: legfeljebb 60 elem. A kódot pontokkal tagold (1, 1.1, 1.1.1). Költséget és elkészültséget csak a munkacsomagokhoz "
        "(a legalsó szinthez) írj; a felsőbb szintek értéke összesítéssel számolódik. A sorokat kód szerint rendezve add meg.",
        "■ Ütemezés: legfeljebb 40 tevékenység, hárompontos becsléssel (optimista, legvalószínűbb, pesszimista, hétben) és legfeljebb négy "
        "előzménnyel. Az előzmény csak korábbi sorban álló tevékenység lehet. A determinisztikus ütemterv a legvalószínűbb időkkel számol; "
        "a PERT a kritikus út várható idejéből és szórásából becsli a határidő teljesülésének valószínűségét.",
        "■ Megszerzett érték: havonta a tervezett érték (PV), a megszerzett érték (EV) és a tényleges költség (AC); SV, CV, SPI, CPI, EAC.",
        "A kitöltött példa a KoboCella-projekt (kézikönyv 26. fejezet).",
        "Források: MIL-STD-881F (2022); PMI: Practice Standard for Work Breakdown Structures (2019); "
        "Kelley és Walker (1959); Malcolm és mtsai (1959); Fleming és Koppelman (2010); NASA Systems Engineering Handbook (2016), 6.1. szakasz és B függelék.",
    ])

    # ---- WBS
    ws = wb.create_sheet("WBS")
    cimsor(ws, "Munkalebontási struktúra", "Költség és elkészültség csak a munkacsomagoknál; a felsőbb szintek összesítése automatikus.")
    fej = ["Kód", "Megnevezés", "Felelős", "Költség [MFt]", "Elkészültség", "Szint", "Szülő", "Munkacsomag?",
           "Összesített költség", "Megszerzett érték", "100%-szabály"]
    K = f"$A$5:$A${4 + NW}"

    def osszes(col):
        return lambda r: (f'=IF(A{r}="","",IF(H{r}="igen",N({col}{r}),SUMIFS(${col}$5:${col}${4 + NW},{K},A{r}&".*",$H$5:$H${4 + NW},"igen")))')

    ut = tablazat(ws, 4, fej, [8, 34, 18, 12, 12, 7, 8, 12, 14, 13, 18], [list(w) for w in WBS],
                  bemeneti_oszlopok=(1, 2, 3, 4, 5),
                  kepletek={6: lambda r: f'=IF(A{r}="","",LEN(A{r})-LEN(SUBSTITUTE(A{r},".",""))+1)',
                            7: lambda r: f'=IF(OR(A{r}="",F{r}=1),"",LEFT(A{r},FIND("@",SUBSTITUTE(A{r},".","@",F{r}-1))-1))',
                            8: lambda r: f'=IF(A{r}="","",IF(COUNTIF({K},A{r}&".*")=0,"igen","nem"))',
                            9: osszes("D"),
                            10: lambda r: (f'=IF(A{r}="","",IF(H{r}="igen",N(D{r})*N(E{r}),'
                                           f'SUMPRODUCT((LEFT($A$5:$A${4 + NW},LEN(A{r})+1)=A{r}&".")*($H$5:$H${4 + NW}="igen")*'
                                           f'$D$5:$D${4 + NW}*$E$5:$E${4 + NW})))'),
                            11: lambda r: (f'=IF(A{r}="","",IF(AND(F{r}>1,COUNTIF({K},G{r})=0),"hiányzó szülő",'
                                           f'IF(AND(H{r}="igen",D{r}=""),"hiányzó költség",IF(AND(H{r}="nem",D{r}<>""),'
                                           f'"a felsőbb szintre ne írj költséget","rendben"))))')},
                  uressor=NW - len(WBS), formatumok={4: "0.0", 5: "0%", 9: "0.0", 10: "0.0"})
    ws.conditional_formatting.add(f"K5:K{ut}", FormulaRule(formula=['AND(K5<>"",K5<>"rendben")'], fill=PatternFill("solid", fgColor="F6D5D5")))
    ws.conditional_formatting.add(f"A5:B{ut}", FormulaRule(formula=["$F5=1"], font=Font(name=BETU, bold=True, color=KEK)))
    szoveg(ws.cell(row=ut + 2, column=2), "Teljes költségvetés (BAC) [MFt]", felkov=True)
    keplet(ws.cell(row=ut + 2, column=4), f'=SUMIFS(D5:D{ut},H5:H{ut},"igen")', "0.0", True)
    szoveg(ws.cell(row=ut + 3, column=2), "Megszerzett érték összesen (EV) [MFt]", felkov=True)
    keplet(ws.cell(row=ut + 3, column=4), f'=SUMPRODUCT((H5:H{ut}="igen")*D5:D{ut}*E5:E{ut})', "0.0", True)
    szoveg(ws.cell(row=ut + 4, column=2), "Ellenőrzés: a legfelső szintek összege = BAC?", felkov=True)
    keplet(ws.cell(row=ut + 4, column=4), f'=IF(ABS(SUMIFS(I5:I{ut},F5:F{ut},1)-D{ut + 2})<0.0001,"igen","nem")', None, True)
    ws.freeze_panes = "C5"
    W_UT = ut

    # ---- Ütemezés
    wt = wb.create_sheet("Ütemezés")
    cimsor(wt, "Hálós ütemterv (CPM) és PERT", "Időegység: hét. Az előzmény csak korábbi sorban álló tevékenység lehet.")
    szoveg(wt["A3"], "Jóváhagyott időtartam [hét]", felkov=True)
    bemenet(wt["C3"], CEL_HET, "0.0")
    fej = ["Az.", "Tevékenység", "WBS", "Opt.", "Legval.", "Pessz.", "Várható (te)", "Szórás",
           "Előzm. 1", "Előzm. 2", "Előzm. 3", "Előzm. 4", "ES", "EF", "LS", "LF", "Tartalék", "Kritikus?", "σ²"]
    r0, r1 = 7, 6 + NT
    END = "$C$4"
    szoveg(wt["A4"], "A projekt időtartama (CPM) [hét]", felkov=True)
    keplet(wt["C4"], f"=MAX(N{r0}:N{r1})", "0.0", True)

    def es(r):
        if r == r0:
            return f'=IF(A{r}="","",0)'
        parts = ",".join(f'IFERROR(INDEX($N${r0}:N{r - 1},MATCH({c}{r},$A${r0}:A{r - 1},0)),0)' for c in "IJKL")
        return f'=IF(A{r}="","",MAX({parts}))'

    def lf(r):
        if r == r1:
            return f'=IF(A{r}="","",{END})'
        cnt = "+".join(f"COUNTIF({c}{r + 1}:{c}${r1},A{r})" for c in "IJKL")
        mins = ",".join(f"IF(COUNTIF({c}{r + 1}:{c}${r1},A{r})>0,_xlfn.MINIFS(O{r + 1}:O${r1},{c}{r + 1}:{c}${r1},A{r}),1E+9)" for c in "IJKL")
        return f'=IF(A{r}="","",IF({cnt}=0,{END},MIN({mins})))'

    sorok = [[t[0], t[1], t[2], t[3], t[4], t[5], None, None] + (t[6] + [None] * NP)[:NP] for t in TEV]
    fejlec(wt, 6, fej, [6, 34, 6, 6, 7, 7, 9, 7, 8, 8, 8, 8, 6, 6, 6, 6, 8, 9, 7])
    for i in range(NT):
        r = r0 + i
        adat = sorok[i] if i < len(sorok) else [None] * 12
        for j in range(12):
            c = wt.cell(row=r, column=1 + j)
            if j in (6, 7):
                continue
            bemenet(c, adat[j], "0.0" if j in (3, 4, 5) else None)
        keplet(wt.cell(row=r, column=7), f'=IF(A{r}="","",(D{r}+4*E{r}+F{r})/6)', "0.00")
        keplet(wt.cell(row=r, column=8), f'=IF(A{r}="","",(F{r}-D{r})/6)', "0.00")
        keplet(wt.cell(row=r, column=13), es(r), "0.0")
        keplet(wt.cell(row=r, column=14), f'=IF(A{r}="","",M{r}+E{r})', "0.0")
        keplet(wt.cell(row=r, column=16), lf(r), "0.0")
        keplet(wt.cell(row=r, column=15), f'=IF(A{r}="","",P{r}-E{r})', "0.0")
        keplet(wt.cell(row=r, column=17), f'=IF(A{r}="","",O{r}-M{r})', "0.0")
        keplet(wt.cell(row=r, column=18), f'=IF(A{r}="","",IF(ABS(Q{r})<0.001,"igen",""))', None, True)
        keplet(wt.cell(row=r, column=19), f'=IF(A{r}="","",H{r}^2)', "0.000")
    wt.conditional_formatting.add(f"R{r0}:R{r1}", FormulaRule(formula=[f'R{r0}="igen"'], fill=PatternFill("solid", fgColor="F4D9A8")))
    g0 = 20
    for k in range(RACS):
        c = wt.cell(row=6, column=g0 + k, value=k + 1)
        c.font, c.fill, c.alignment, c.border = fej_font, fej_fill, kozep, keret
        wt.column_dimensions[get_column_letter(g0 + k)].width = 3.0
        for r in range(r0, r1 + 1):
            cc = wt.cell(row=r, column=g0 + k)
            cc.value = f'=IF($A{r}="","",IF(AND({k + 1}>$M{r},{k + 1}<=$N{r}),IF($R{r}="igen",2,1),""))'
            cc.number_format = ";;;"
            cc.border = keret
    zona = f"{get_column_letter(g0)}{r0}:{get_column_letter(g0 + RACS - 1)}{r1}"
    wt.conditional_formatting.add(zona, FormulaRule(formula=[f"{get_column_letter(g0)}{r0}=2"], fill=PatternFill("solid", fgColor=KEK)))
    wt.conditional_formatting.add(zona, FormulaRule(formula=[f"{get_column_letter(g0)}{r0}=1"], fill=PatternFill("solid", fgColor="A9C4DE")))
    p0 = r1 + 2
    szoveg(wt.cell(row=p0, column=2), "PERT a kritikus úton", felkov=True)
    pert = [("A kritikus út várható ideje (Σ te) [hét]", f'=SUMIFS(G{r0}:G{r1},R{r0}:R{r1},"igen")', "0.0"),
            ("A kritikus út szórása (√Σσ²) [hét]", f'=SQRT(SUMIFS(S{r0}:S{r1},R{r0}:R{r1},"igen"))', "0.00"),
            ("P(befejezés ≤ jóváhagyott időtartam)", f"=NORMSDIST(($C$3-C{p0 + 1})/C{p0 + 2})", "0.0%")]
    for i, (n, f, fm) in enumerate(pert):
        szoveg(wt.cell(row=p0 + 1 + i, column=2), n)
        keplet(wt.cell(row=p0 + 1 + i, column=3), f, fm, True)
    megjegyzes(wt.cell(row=p0 + 3, column=2), "A klasszikus PERT csak a kritikus utat veszi figyelembe, ezért a valószínűséget általában túlbecsli; "
                                              "a párhuzamos, közel kritikus utak hatását a notebook Monte Carlo-szimulációja mutatja.")
    wt.freeze_panes = "C7"

    # ---- Megszerzett érték
    we = wb.create_sheet("Megszerzett érték")
    cimsor(we, "Megszerzett érték (EVM)", "Kumulált értékek hónaponként [MFt]; a tényleges értékeket csak az elmúlt hónapokra írd be.")
    szoveg(we["A3"], "Teljes költségvetés (BAC)", felkov=True)
    keplet(we["C3"], f"='WBS'!D{W_UT + 2}", "0.0", True)
    fej = ["Hónap", "PV", "EV", "AC", "SV = EV − PV", "CV = EV − AC", "SPI = EV/PV", "CPI = EV/AC", "EAC = BAC/CPI"]
    sorok = [[h, p, EV[i] if i < len(EV) else None, AC[i] if i < len(AC) else None] for i, (h, p) in enumerate(zip(HONAP, PV))]
    ut = tablazat(we, 5, fej, [8, 10, 10, 10, 13, 13, 12, 12, 14], sorok, bemeneti_oszlopok=(1, 2, 3, 4),
                  kepletek={5: lambda r: f'=IF(OR(C{r}="",B{r}=""),"",C{r}-B{r})',
                            6: lambda r: f'=IF(OR(C{r}="",D{r}=""),"",C{r}-D{r})',
                            7: lambda r: f'=IF(OR(C{r}="",N(B{r})=0),"",C{r}/B{r})',
                            8: lambda r: f'=IF(OR(C{r}="",N(D{r})=0),"",C{r}/D{r})',
                            9: lambda r: f'=IF(H{r}="","",$C$3/H{r})'},
                  uressor=NH - len(PV), formatumok={2: "0.0", 3: "0.0", 4: "0.0", 5: "0.0", 6: "0.0", 7: "0.00", 8: "0.00", 9: "0.0"})
    we.conditional_formatting.add(f"G6:H{ut}", FormulaRule(formula=["AND(ISNUMBER(G6),G6<0.95)"], fill=PatternFill("solid", fgColor="F6D5D5")))
    we.conditional_formatting.add(f"G6:H{ut}", FormulaRule(formula=["AND(ISNUMBER(G6),G6>=0.95,G6<1)"], fill=PatternFill("solid", fgColor="FFF4CC")))
    megjegyzes(we["G5"], "Színkód: piros < 0,95; sárga 0,95–1,00; a színkódos jelzőzónák a mérőszámok gyors áttekintését segítik.")
    szoveg(we.cell(row=ut + 2, column=1), "Ellenőrzés: az utolsó EV egyezik a WBS megszerzett értékével?", felkov=True)
    keplet(we.cell(row=ut + 2, column=9),
           f"=IF(COUNT(C6:C{ut})=0,\"\",IF(ABS(INDEX(C6:C{ut},COUNT(C6:C{ut}))-'WBS'!D{W_UT + 3})<0.05,\"igen\",\"nem\"))", None, True)
    ch = LineChart()
    diagram_kozos(ch, "Tervezett érték, megszerzett érték, tényleges költség", "hónap", "MFt", 20, 10)
    ch.add_data(Reference(we, min_col=2, max_col=4, min_row=5, max_row=5 + len(PV)), titles_from_data=True)
    ch.set_categories(Reference(we, min_col=1, min_row=6, max_row=5 + len(PV)))
    we.add_chart(ch, "K3")
    return mentes(wb, "wbs_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
