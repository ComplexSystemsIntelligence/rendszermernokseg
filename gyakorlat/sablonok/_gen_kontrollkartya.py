"""Kontrollkártyák (X̄–R és egyedi értékes) és folyamatképesség (eszközlap: Kontrollkártya)."""
from openpyxl.formatting.rule import FormulaRule

from _kozos import *  # noqa: F401,F403
from _spc_adat import ALLANDOK, FORGACS, FORGACS_I, KOBO, KOBO_I, TURES

NR, NM, NI = 50, 10, 100
PIROS = PatternFill("solid", fgColor="F6D5D5")


def sz(cell, op, lim):
    return f"IF(ISNUMBER({cell}),{cell}{op}{lim},FALSE)"


def szabalyok(oszlop, r, r0, cl, u1, l1, u2, l2, u3, l3):
    """A Western Electric-szabályok közül négy egy sorra (r: aktuális sor, r0: első adatsor)."""
    x = f"{oszlop}{r}"
    s1 = f"OR({sz(x, '>', u3)},{sz(x, '<', l3)})"
    def k(n, lim, op):
        return "+".join(f"({sz(f'{oszlop}{r - j}', op, lim)})" for j in range(n))
    s2 = (f"OR(AND({sz(x, '>', u2)},{k(3, u2, '>')}>=2),AND({sz(x, '<', l2)},{k(3, l2, '<')}>=2))" if r - r0 >= 2 else "FALSE")
    s3 = (f"OR(AND({sz(x, '>', u1)},{k(5, u1, '>')}>=4),AND({sz(x, '<', l1)},{k(5, l1, '<')}>=4))" if r - r0 >= 4 else "FALSE")
    s4 = (f"OR({k(8, cl, '>')}=8,{k(8, cl, '<')}=8)" if r - r0 >= 7 else "FALSE")
    return s1, s2, s3, s4


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Kontrollkártya és folyamatképesség – sablon", [
        "■ Mire való? Egy folyamatjellemző időbeli stabilitásának figyelése: a véletlen ingadozás elkülönítése a különleges okoktól "
        "(Shewhart), és a folyamatképesség (Cp, Cpk) számítása a tűréshez viszonyítva.",
        "■ X–R: legfeljebb 50 részcsoport, részcsoportonként 2–10 mérés (például óránként öt egymást követő darab). Add meg a "
        "részcsoport méretét, az I. szakasz (a határok számítása) részcsoportjainak számát és a tűréshatárokat.",
        "■ Egyedi (I-MR): ha egyszerre csak egy érték keletkezik (napi mutató, adagonkénti mérés); legfeljebb 100 érték.",
        "■ Jelzések (Western Electric-szabályok, Montgomery 2020): 1 = egy pont a ±3σ határon kívül; 2 = három egymást követő pontból kettő ugyanazon az oldalon "
        "a 2σ-n túl; 3 = öt egymást követő pontból négy ugyanazon az oldalon az 1σ-n túl; 4 = nyolc egymást követő pont a középvonal "
        "ugyanazon oldalán; R = a terjedelem a felső határ fölött.",
        "■ Képesség: Cp és Cpk a részcsoporton belüli szórásból, Pp és Ppk az összes egyedi érték szórásából. Csak stabil folyamatra értelmezhető.",
        "■ A diagramok az első 25 részcsoportot (X–R), illetve 40 értéket (I-MR) mutatják; több adatnál bővítsd a diagram tartományát.",
        "A kitöltött példák: a KoboCella csavarozási nyomatéka és a ForgácsTech napi anyagra várása (kézikönyv 25. fejezet).",
        "Források: Shewhart (1931); Montgomery: Introduction to Statistical Quality Control (2020); NASA RP-1358 (1994), 7.14. szakasz.",
    ])

    # ---- Állandók
    wa = wb.create_sheet("Állandók")
    cimsor(wa, "A Shewhart-kártyák állandói", "Montgomery (2020), VI. függelék.")
    tablazat(wa, 4, ["n", "d2", "A2", "D3", "D4"], [6, 9, 9, 9, 9],
             [[n, *v] for n, v in ALLANDOK.items()], formatumok={2: "0.000", 3: "0.000", 4: "0.000", 5: "0.000"})
    TAB = "'Állandók'!$A$5:$E$13"

    # ---- X–R
    ws = wb.create_sheet("X–R")
    cimsor(ws, "Átlag- és terjedelemkártya (X̄–R)", "KoboCella: óránként öt egymást követő kötés nyomatéka [Nm].")
    be = [("Részcsoport mérete (n)", 5, "0"), ("Az I. szakasz részcsoportjai", KOBO_I, "0"),
          ("Alsó tűréshatár (ATH)", TURES[0], "0.000"), ("Felső tűréshatár (FTH)", TURES[1], "0.000")]
    ws.column_dimensions["A"].width = 28
    for i, (n, v, f) in enumerate(be):
        szoveg(ws.cell(row=3 + i, column=1), n)
        bemenet(ws.cell(row=3 + i, column=2), v, f)
    r0, r1 = 9, 8 + NR
    N_ = f"$N${r0}:INDEX($N${r0}:$N${r1},$B$4)"
    O_ = f"$O${r0}:INDEX($O${r0}:$O${r1},$B$4)"
    hat = [("X̄̄ (középvonal)", f"=AVERAGE({N_})", "0.0000"), ("R̄", f"=AVERAGE({O_})", "0.0000"),
           ("σ̂ = R̄/d2", f"=E4/VLOOKUP($B$3,{TAB},2,FALSE)", "0.0000"), ("σ az átlagra", "=E5/SQRT($B$3)", "0.0000")]
    for i, (n, f, fmt) in enumerate(hat):
        szoveg(ws.cell(row=3 + i, column=4), n)
        keplet(ws.cell(row=3 + i, column=5), f, fmt, True)
    hat2 = [("FEH (X̄)", f"=E3+VLOOKUP($B$3,{TAB},3,FALSE)*E4", "0.0000"), ("AEH (X̄)", f"=E3-VLOOKUP($B$3,{TAB},3,FALSE)*E4", "0.0000"),
            ("FEH (R)", f"=VLOOKUP($B$3,{TAB},5,FALSE)*E4", "0.0000"), ("AEH (R)", f"=VLOOKUP($B$3,{TAB},4,FALSE)*E4", "0.0000")]
    for i, (n, f, fmt) in enumerate(hat2):
        szoveg(ws.cell(row=3 + i, column=6), n)
        keplet(ws.cell(row=3 + i, column=7), f, fmt, True)
    zon = [("+2σ", "=E3+2*E6"), ("−2σ", "=E3-2*E6"), ("+1σ", "=E3+E6"), ("−1σ", "=E3-E6")]
    for i, (n, f) in enumerate(zon):
        szoveg(ws.cell(row=3 + i, column=8), n)
        keplet(ws.cell(row=3 + i, column=9), f, "0.0000")
    for c, w in zip("DEFGHI", [16, 10, 10, 10, 6, 10]):
        ws.column_dimensions[c].width = w
    fej = ["Részcsoport", "Időpont"] + [f"x{j + 1}" for j in range(NM)] + ["db", "Átlag", "Terjedelem", "CL", "FEH", "AEH",
                                                                 "1", "2", "3", "4", "R", "Jelzés"]
    fejlec(ws, 8, fej, None)
    ws.column_dimensions["B"].width = 10
    for j in range(NM):
        ws.column_dimensions[get_column_letter(3 + j)].width = 7
    for cl_, w in zip(["M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X"], [5, 9, 10, 8, 8, 8, 5, 5, 5, 5, 5, 12]):
        ws.column_dimensions[cl_].width = w
    for i in range(NR):
        r = r0 + i
        szoveg(ws.cell(row=r, column=1), i + 1)
        bemenet(ws.cell(row=r, column=2), f"{6 + i % 8}:00 ({i // 8 + 1}. műszak)" if i < len(KOBO) else None)
        for j in range(NM):
            v = KOBO[i][j] if i < len(KOBO) and j < len(KOBO[i]) else None
            bemenet(ws.cell(row=r, column=3 + j), v, "0.000")
        X = f"C{r}:L{r}"
        keplet(ws.cell(row=r, column=13), f"=COUNT({X})", "0")
        keplet(ws.cell(row=r, column=14), f'=IF(M{r}<2,"",AVERAGE({X}))', "0.0000")
        keplet(ws.cell(row=r, column=15), f'=IF(M{r}<2,"",MAX({X})-MIN({X}))', "0.000")
        keplet(ws.cell(row=r, column=16), f'=IF(N{r}="","",$E$3)', "0.000")
        keplet(ws.cell(row=r, column=17), f'=IF(N{r}="","",$G$3)', "0.000")
        keplet(ws.cell(row=r, column=18), f'=IF(N{r}="","",$G$4)', "0.000")
        s = szabalyok("N", r, r0, "$E$3", "$I$5", "$I$6", "$I$3", "$I$4", "$G$3", "$G$4")
        for k, f in enumerate(s):
            keplet(ws.cell(row=r, column=19 + k), f'=IF(N{r}="","",IF({f},1,""))', "0")
        keplet(ws.cell(row=r, column=23), f'=IF(O{r}="","",IF(O{r}>$G$5,1,""))', "0")
        keplet(ws.cell(row=r, column=24),
               f'=IF(N{r}="","",IF(COUNT(S{r}:W{r})=0,"",IF(S{r}=1,"1 ","")&IF(T{r}=1,"2 ","")&IF(U{r}=1,"3 ","")&IF(V{r}=1,"4 ","")&IF(W{r}=1,"R","")))')
    ws.conditional_formatting.add(f"X{r0}:X{r1}", FormulaRule(formula=[f'LEN(X{r0})>0'], fill=PIROS))
    ws.conditional_formatting.add(f"A{r0}:A{r1}", FormulaRule(formula=[f"A{r0}<=$B$4"], fill=PatternFill("solid", fgColor="E6EEF6")))
    ws.freeze_panes = "C9"
    ch = LineChart()
    diagram_kozos(ch, "Átlagkártya", "részcsoport", "átlag", 24, 10)
    for col in (14, 16, 17, 18):
        ch.add_data(Reference(ws, min_col=col, min_row=8, max_row=8 + 25), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=r0, max_row=8 + 25))
    ch.y_axis.scaling.min, ch.y_axis.scaling.max = 3.90, 4.12
    ws.add_chart(ch, "Z3")
    ch2 = LineChart()
    diagram_kozos(ch2, "Terjedelemkártya", "részcsoport", "terjedelem", 24, 7)
    ch2.add_data(Reference(ws, min_col=15, min_row=8, max_row=8 + 25), titles_from_data=True)
    ch2.set_categories(Reference(ws, min_col=1, min_row=r0, max_row=8 + 25))
    ws.add_chart(ch2, "Z24")

    # ---- Egyedi (I-MR)
    wi = wb.create_sheet("Egyedi (I-MR)")
    cimsor(wi, "Egyedi értékes és mozgóterjedelem-kártya (I-MR)", "ForgácsTech: napi anyagra várás [perc] a fejlesztés után.")
    wi.column_dimensions["A"].width = 28
    szoveg(wi["A3"], "Az I. szakasz értékei")
    bemenet(wi["B3"], FORGACS_I, "0")
    szoveg(wi["A4"], "Alsó határ nem lehet negatív?")
    bemenet(wi["B4"], "igen")
    legordulo(wi, "B4", ["igen", "nem"])
    j0, j1 = 12, 11 + NI
    V_ = f"$B${j0}:INDEX($B${j0}:$B${j1},$B$3)"
    M_ = f"$C${j0 + 1}:INDEX($C${j0}:$C${j1},$B$3)"
    ih = [("Középvonal (X̄)", f"=AVERAGE({V_})"), ("MR̄", f"=AVERAGE({M_})"), ("σ̂ = MR̄/1,128", "=E4/1.128"),
          ("FEH (X)", "=E3+3*E5"), ("AEH (X)", '=IF(AND($B$4="igen",E3-3*E5<0),0,E3-3*E5)'), ("FEH (MR)", "=3.267*E4")]
    for i, (n, f) in enumerate(ih):
        szoveg(wi.cell(row=3 + i, column=4), n)
        keplet(wi.cell(row=3 + i, column=5), f, "0.00", True)
    wi.column_dimensions["D"].width = 18
    fej = ["Sorszám", "Érték", "Mozgó terjedelem", "CL", "FEH", "AEH", "1", "4", "MR", "Jelzés"]
    fejlec(wi, 11, fej, [9, 10, 12, 8, 8, 8, 5, 5, 5, 12])
    for i in range(NI):
        r = j0 + i
        szoveg(wi.cell(row=r, column=1), i + 1)
        bemenet(wi.cell(row=r, column=2), FORGACS[i] if i < len(FORGACS) else None, "0")
        keplet(wi.cell(row=r, column=3), "" if i == 0 else f'=IF(OR(B{r}="",B{r - 1}=""),"",ABS(B{r}-B{r - 1}))', "0")
        keplet(wi.cell(row=r, column=4), f'=IF(B{r}="","",$E$3)', "0.0")
        keplet(wi.cell(row=r, column=5), f'=IF(B{r}="","",$E$6)', "0.0")
        keplet(wi.cell(row=r, column=6), f'=IF(B{r}="","",$E$7)', "0.0")
        s1, _, _, s4 = szabalyok("B", r, j0, "$E$3", "$E$3", "$E$3", "$E$3", "$E$3", "$E$6", "$E$7")
        keplet(wi.cell(row=r, column=7), f'=IF(B{r}="","",IF({s1},1,""))', "0")
        keplet(wi.cell(row=r, column=8), f'=IF(B{r}="","",IF({s4},1,""))', "0")
        keplet(wi.cell(row=r, column=9), f'=IF(C{r}="","",IF(C{r}>$E$8,1,""))', "0")
        keplet(wi.cell(row=r, column=10), f'=IF(B{r}="","",IF(COUNT(G{r}:I{r})=0,"",IF(G{r}=1,"1 ","")&IF(H{r}=1,"4 ","")&IF(I{r}=1,"MR","")))')
    wi.conditional_formatting.add(f"J{j0}:J{j1}", FormulaRule(formula=[f'LEN(J{j0})>0'], fill=PIROS))
    wi.freeze_panes = "B12"
    ch = LineChart()
    diagram_kozos(ch, "Egyedi értékes kártya", "nap", "perc", 24, 10)
    for col in (2, 4, 5, 6):
        ch.add_data(Reference(wi, min_col=col, min_row=11, max_row=11 + 40), titles_from_data=True)
    ch.set_categories(Reference(wi, min_col=1, min_row=j0, max_row=11 + 40))
    wi.add_chart(ch, "L3")

    # ---- Képesség
    wk = wb.create_sheet("Képesség")
    cimsor(wk, "Folyamatképesség (az X–R lap I. szakaszából)", "Csak stabil (jelzés nélküli) folyamatra értelmezhető.")
    wk.column_dimensions["A"].width = 52
    wk.column_dimensions["B"].width = 14
    XR = "'X–R'!"
    osszes = f"{XR}$C${r0}:INDEX({XR}$L${r0}:$L${r1},{XR}$B$4)"
    k = [("Középérték (X̄̄)", f"={XR}E3", "0.0000"), ("Részcsoporton belüli szórás (σ̂ = R̄/d2)", f"={XR}E5", "0.0000"),
         ("Teljes szórás (az összes egyedi érték, s)", f"=STDEV({osszes})", "0.0000"),
         ("Cp = (FTH − ATH) / 6σ̂", f"=({XR}B6-{XR}B5)/(6*B5)", "0.00"),
         ("Cpk = min(FTH − X̄̄, X̄̄ − ATH) / 3σ̂", f"=MIN({XR}B6-B4,B4-{XR}B5)/(3*B5)", "0.00"),
         ("Pp = (FTH − ATH) / 6s", f"=({XR}B6-{XR}B5)/(6*B6)", "0.00"),
         ("Ppk = min(FTH − X̄̄, X̄̄ − ATH) / 3s", f"=MIN({XR}B6-B4,B4-{XR}B5)/(3*B6)", "0.00"),
         ("Jelzések száma az I. szakaszban", f"=COUNTIF({XR}$X${r0}:INDEX({XR}$X${r0}:$X${r1},{XR}$B$4),\"?*\")", "0"),
         ("Értékelés", '=IF(B11>0,"az I. szakasz nem stabil: előbb a különleges okokat kell megszüntetni",'
                       'IF(B8>=1.33,"a Cpk legalább 1,33 (Montgomery ajánlott minimuma meglévő folyamatra)","a Cpk 1,33 alatt: javítandó"))', None)]
    for i, (n, f, fmt) in enumerate(k):
        szoveg(wk.cell(row=4 + i, column=1), n)
        keplet(wk.cell(row=4 + i, column=2), f, fmt, i in (4, 7, 8))
    wk.merge_cells("B12:F12")
    megjegyzes(wk["A8"], "Montgomery (2020) ajánlott minimumai: meglévő folyamat 1,33; új folyamat 1,50; biztonsági vagy kritikus "
                         "jellemző meglévő folyamatnál 1,50, újnál 1,67.")
    return mentes(wb, "kontrollkartya_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
