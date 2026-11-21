"""Hisztogram, rétegzés és szórásdiagram (eszközlap: Hisztogram, szórás- és rétegzett diagram)."""
from openpyxl.formatting.rule import FormulaRule

from _hisztogram_adat import ADAT, TURES
from _kozos import *  # noqa: F401,F403

NA, NB, NS = 300, 20, 3


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Hisztogram, rétegzés és szórásdiagram – sablon", [
        "■ Mire való? Egy mért jellemző eloszlásának vizsgálata (hisztogram, leíró statisztikák, a tűrésmezőhöz viszonyított helyzet), "
        "az adatok rétegzése (például tétel, gép, műszak szerint) és két változó kapcsolatának vizsgálata (szórásdiagram, korreláció, regresszió).",
        "■ Adatok: legfeljebb 300 sor: réteg (legfeljebb 3 különböző), X (magyarázó változó, opcionális), Y (a vizsgált jellemző).",
        "■ Statisztika: leíró statisztikák összesen és rétegenként; a Pp, Ppk a teljes szórással számol (a kontrollkártya Cp, Cpk "
        "indexéhez a részcsoporton belüli szórás kell).",
        "■ Hisztogram: add meg az első osztály alsó határát és az osztályszélességet (legfeljebb 20 osztály). A tűrésmezőn kívüli osztályok "
        "pirosak. A rétegzett hisztogram a rétegeket egymásra halmozva mutatja.",
        "■ Szórásdiagram: X és Y kapcsolata, korrelációs együttható, a t-próba p-értéke és a regressziós egyenes, összesen és rétegenként.",
        "A kitöltött példa a KoboCella két beérkező csavartételének csavarozási próbája (kézikönyv 25. fejezet).",
        "Források: Ishikawa (1982); Montgomery: Introduction to Statistical Quality Control (2020); NASA RP-1358 (1994), 5.1., 5.5. és 5.7. szakasz.",
    ])

    # ---- Adatok
    ws = wb.create_sheet("Adatok")
    cimsor(ws, "Adatok", "X: a bitbetéttel addig végzett csavarozások száma [ezer]; Y: nyomaték [Nm].")
    ut = tablazat(ws, 4, ["Sorszám", "Réteg", "X", "Y"], [9, 14, 10, 10], [list(r) for r in ADAT],
                  bemeneti_oszlopok=(2, 3, 4), uressor=NA - len(ADAT), formatumok={3: "0.0", 4: "0.000"})
    ws.freeze_panes = "A5"
    A_UT = ut
    G, X, Y = f"'Adatok'!$B$5:$B${A_UT}", f"'Adatok'!$C$5:$C${A_UT}", f"'Adatok'!$D$5:$D${A_UT}"

    # ---- Statisztika
    st = wb.create_sheet("Statisztika")
    cimsor(st, "Leíró statisztikák", "A rétegek nevét a C4:E4 cellákba írd (pontosan úgy, ahogy az Adatok lapon szerepelnek).")
    st.column_dimensions["A"].width = 34
    for c in "BCDE":
        st.column_dimensions[c].width = 13
    szoveg(st["A3"], "Alsó tűréshatár (ATH)")
    bemenet(st["B3"], TURES[0], "0.000")
    szoveg(st["C3"], "Felső tűréshatár (FTH)")
    bemenet(st["D3"], TURES[1], "0.000")
    fejlec(st, 4, ["Mutató", "Összesen"])
    retegek = sorted({r[1] for r in ADAT})
    for j in range(NS):
        bemenet(st.cell(row=4, column=3 + j), retegek[j] if j < len(retegek) else None)
    sorok = ["n", "Átlag", "Szórás (s)", "Minimum", "Maximum", "Medián", "Pp = (FTH − ATH)/6s", "Ppk = min(FTH − átlag, átlag − ATH)/3s",
             "Tűrésen kívüli darab"]
    for i, n in enumerate(sorok):
        szoveg(st.cell(row=5 + i, column=1), n)
    osz = [f"=COUNT({Y})", f"=AVERAGE({Y})", f"=STDEV({Y})", f"=MIN({Y})", f"=MAX({Y})", f"=MEDIAN({Y})",
           "=($D$3-$B$3)/(6*B7)", "=MIN($D$3-B6,B6-$B$3)/(3*B7)", f'=COUNTIF({Y},"<"&$B$3)+COUNTIF({Y},">"&$D$3)']
    fmts = ["0", "0.0000", "0.0000", "0.000", "0.000", "0.000", "0.00", "0.00", "0"]
    for i, (f, fm) in enumerate(zip(osz, fmts)):
        keplet(st.cell(row=5 + i, column=2), f, fm, i in (6, 7))
    for j in range(NS):
        c = get_column_letter(3 + j)
        h = f"{c}$4"
        fs = [f'=IF({h}="","",COUNTIFS({G},{h},{Y},"<>"))',
              f'=IF(OR({h}="",{c}5=0),"",AVERAGEIF({G},{h},{Y}))',
              f'=IF(OR({h}="",N({c}5)<2),"",SQRT(SUMPRODUCT(({G}={h})*({Y}<>"")*({Y}-{c}6)^2)/({c}5-1)))',
              f'=IF(OR({h}="",N({c}5)=0),"",_xlfn.MINIFS({Y},{G},{h}))',
              f'=IF(OR({h}="",N({c}5)=0),"",_xlfn.MAXIFS({Y},{G},{h}))',
              "",
              f'=IF({c}7="","",($D$3-$B$3)/(6*{c}7))',
              f'=IF({c}7="","",MIN($D$3-{c}6,{c}6-$B$3)/(3*{c}7))',
              f'=IF({h}="","",COUNTIFS({G},{h},{Y},"<"&$B$3)+COUNTIFS({G},{h},{Y},">"&$D$3))']
        for i, (f, fm) in enumerate(zip(fs, fmts)):
            if f:
                keplet(st.cell(row=5 + i, column=3 + j), f, fm, i in (6, 7))
            else:
                keplet(st.cell(row=5 + i, column=3 + j), "–")
    megjegyzes(st["A10"], "A rétegenkénti medián tömbképlet nélkül nem számolható; a notebook kiszámolja.")

    # ---- Hisztogram
    hi = wb.create_sheet("Hisztogram")
    cimsor(hi, "Hisztogram és rétegzett hisztogram")
    hi.column_dimensions["A"].width = 26
    szoveg(hi["A3"], "Az első osztály alsó határa")
    bemenet(hi["B3"], 3.82, "0.000")
    szoveg(hi["A4"], "Osztályszélesség")
    bemenet(hi["B4"], 0.02, "0.000")
    megjegyzes(hi["A4"], "Ökölszabály: az osztályok száma kb. a mintaelemszám négyzetgyöke (120 adat → 10–12 osztály).")
    fej = ["Osztály", "Alsó határ", "Felső határ", "Közép", "Összesen"] + [f"=Statisztika!{get_column_letter(3 + j)}4&\"\"" for j in range(NS)]
    fejlec(hi, 6, fej, [26, 10, 10, 10, 10, 11, 11, 11])
    for k in range(NB):
        r = 7 + k
        keplet(hi.cell(row=r, column=1), f'=FIXED(B{r},3,TRUE)&"–"&FIXED(C{r},3,TRUE)')
        keplet(hi.cell(row=r, column=2), f"=$B$3+{k}*$B$4", "0.000")
        keplet(hi.cell(row=r, column=3), f"=B{r}+$B$4", "0.000")
        keplet(hi.cell(row=r, column=4), f"=(B{r}+C{r})/2", "0.000")
        keplet(hi.cell(row=r, column=5), f'=COUNTIFS({Y},">="&B{r},{Y},"<"&C{r})', "0")
        for j in range(NS):
            h = f"Statisztika!${get_column_letter(3 + j)}$4"
            keplet(hi.cell(row=r, column=6 + j), f'=IF({h}="","",COUNTIFS({G},{h},{Y},">="&B{r},{Y},"<"&C{r}))', "0")
    rt = 7 + NB
    szoveg(hi.cell(row=rt, column=1), "Összesen (ellenőrzés)", felkov=True)
    keplet(hi.cell(row=rt, column=5), f"=SUM(E7:E{rt - 1})", "0", True)
    szoveg(hi.cell(row=rt + 1, column=1), "Az osztályokon kívül eső adatok")
    keplet(hi.cell(row=rt + 1, column=5), f"=Statisztika!B5-E{rt}", "0", True)
    hi.conditional_formatting.add(f"A7:A{rt - 1}", FormulaRule(formula=["OR(B7<Statisztika!$B$3,C7>Statisztika!$D$3)"],
                                                              fill=PatternFill("solid", fgColor="F6D5D5")))
    ch = BarChart()
    ch.type, ch.gapWidth = "col", 10
    diagram_kozos(ch, "Hisztogram", "nyomaték [Nm]", "gyakoriság", 20, 9)
    ch.add_data(Reference(hi, min_col=5, min_row=6, max_row=rt - 1), titles_from_data=True)
    ch.set_categories(Reference(hi, min_col=4, min_row=7, max_row=rt - 1))
    ch.legend = None
    hi.add_chart(ch, "J3")
    ch2 = BarChart()
    ch2.type, ch2.grouping, ch2.overlap, ch2.gapWidth = "col", "stacked", 100, 10
    diagram_kozos(ch2, "Rétegzett hisztogram", "nyomaték [Nm]", "gyakoriság", 20, 9)
    ch2.add_data(Reference(hi, min_col=6, max_col=5 + len(retegek), min_row=6, max_row=rt - 1), titles_from_data=True)
    ch2.set_categories(Reference(hi, min_col=4, min_row=7, max_row=rt - 1))
    hi.add_chart(ch2, "J23")

    # ---- Szórásdiagram
    sd = wb.create_sheet("Szórásdiagram")
    cimsor(sd, "Szórásdiagram, korreláció és regresszió", "Y = a + b·X; a p-érték a korreláció t-próbájából (H0: nincs kapcsolat).")
    sd.column_dimensions["A"].width = 30
    for c in "BCDE":
        sd.column_dimensions[c].width = 13
    fejlec(sd, 4, ["Mutató", "Összesen"] + [f"=Statisztika!{get_column_letter(3 + j)}4&\"\"" for j in range(NS)])
    nev = ["n (X és Y is kitöltve)", "Korrelációs együttható (r)", "Meredekség (b)", "Tengelymetszet (a)", "Determinációs együttható (r²)",
           "t-érték", "p-érték (kétoldali)"]
    for i, n in enumerate(nev):
        szoveg(sd.cell(row=5 + i, column=1), n)
    tot = [f'=SUMPRODUCT(({X}<>"")*({Y}<>""))', f"=CORREL({X},{Y})", f"=SLOPE({Y},{X})", f"=INTERCEPT({Y},{X})", "=B6^2",
           '=IF(OR(B5<3,ABS(B6)>=1),"",B6*SQRT(B5-2)/SQRT(1-B6^2))', '=IF(B10="","",TDIST(ABS(B10),B5-2,2))']
    fm = ["0", "0.000", "0.00000", "0.0000", "0.000", "0.00", "0.0000"]
    for i, (f, f_) in enumerate(zip(tot, fm)):
        keplet(sd.cell(row=5 + i, column=2), f, f_, i in (1, 6))
    for j in range(NS):
        c = get_column_letter(3 + j)
        h = f"{c}$4"
        m = f"({G}={h})*({X}<>\"\")*({Y}<>\"\")"
        mx = f"AVERAGEIFS({X},{G},{h},{Y},\"<>\")"
        my = f"AVERAGEIFS({Y},{G},{h},{X},\"<>\")"
        sxy = f"SUMPRODUCT({m}*({X}-{mx})*({Y}-{my}))"
        sxx = f"SUMPRODUCT({m}*({X}-{mx})^2)"
        syy = f"SUMPRODUCT({m}*({Y}-{my})^2)"
        fs = [f'=IF({h}="","",SUMPRODUCT({m}))',
              f'=IF(N({c}5)<3,"",{sxy}/SQRT({sxx}*{syy}))',
              f'=IF(N({c}5)<3,"",{sxy}/{sxx})',
              f'=IF(N({c}5)<3,"",{my}-{c}7*{mx})',
              f'=IF({c}6="","",{c}6^2)',
              f'=IF(OR({c}6="",ABS(N({c}6))>=1),"",{c}6*SQRT({c}5-2)/SQRT(1-{c}6^2))',
              f'=IF({c}10="","",TDIST(ABS({c}10),{c}5-2,2))']
        for i, (f, f_) in enumerate(zip(fs, fm)):
            keplet(sd.cell(row=5 + i, column=3 + j), f, f_, i in (1, 6))
    szoveg(sd["A13"], "Olvasat: a korreláció nem bizonyít ok-okozati kapcsolatot; rétegzés nélkül a rétegek közötti különbség "
                      "látszólagos kapcsolatot okozhat vagy elfedhet.")
    sd.merge_cells("A13:E13")
    sc = ScatterChart()
    diagram_kozos(sc, "Szórásdiagram", "X (csavarozások a bitbetéttel, ezer)", "Y (nyomaték, Nm)", 20, 10)
    sc.style = 13
    for t in retegek:
        idx = [i for i, r in enumerate(ADAT) if r[1] == t]
        s_ = Series(Reference(ws, min_col=4, min_row=5 + idx[0], max_row=5 + idx[-1]),
                    Reference(ws, min_col=3, min_row=5 + idx[0], max_row=5 + idx[-1]), title=t)
        s_.marker.symbol = "circle"
        s_.graphicalProperties.line.noFill = True
        sc.series.append(s_)
    sc.y_axis.scaling.min, sc.y_axis.scaling.max = 3.80, 4.20
    sd.add_chart(sc, "G3")
    return mentes(wb, "hisztogram_szoras_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
