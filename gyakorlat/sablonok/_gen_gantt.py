"""Gantt-diagram és ütemezés (eszközlap: Gantt-diagram és ütemezés)."""
from openpyxl.formatting.rule import FormulaRule

from _kozos import *  # noqa: F401,F403

EGY = [("R1", 6, 20), ("R2", 2, 6), ("R3", 8, 30), ("R4", 3, 10), ("R5", 5, 12), ("R6", 4, 24)]
KET = [("A", 4, 2), ("B", 1, 3), ("C", 5, 4), ("D", 2, 1), ("E", 3, 5)]
N1, N2 = 20, 15
SZABALYOK = ["FCFS", "SPT", "EDD", "CR", "kézi"]
RACS = 40


def racs(ws, sor, cim, idk, kezd, veg, lepes_cella, oszlop0=3):
    """Időrács: a cellában annak a feladatnak az azonosítója áll, amely az adott időben fut (LOOKUP rendezett kezdési időkön)."""
    szoveg(ws.cell(row=sor, column=1), cim, felkov=True)
    for k in range(RACS):
        c = ws.cell(row=sor, column=oszlop0 + k)
        t = f"(({k}+0.5)*{lepes_cella})"
        c.value = (f'=IFERROR(IF(LOOKUP({t},{kezd},{veg})>{t},LOOKUP({t},{kezd},{idk}),""),"")')
        c.font = Font(name=BETU, size=8, bold=True, color="FFFFFF")
        c.alignment = kozep
        c.border = keret
        ws.column_dimensions[get_column_letter(oszlop0 + k)].width = 3.2
    ws.conditional_formatting.add(f"{get_column_letter(oszlop0)}{sor}:{get_column_letter(oszlop0 + RACS - 1)}{sor}",
                                  FormulaRule(formula=[f'LEN({get_column_letter(oszlop0)}{sor})>0'], fill=PatternFill("solid", fgColor=KEK)))


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Gantt-diagram és ütemezés – sablon", [
        "■ Mire való? Munkafeladatok sorrendjének meghatározása és összevetése egy gépen (FCFS, SPT, EDD, CR vagy kézi sorrend), illetve két egymást követő gépen (Johnson-eljárás), Gantt-diagrammal (kézikönyv 21. fejezet; Lakatos: Termelési rendszerek, 6.3; Johnson, 1954).",
        "1. Az „Egy gép” lapon soronként egy munkafeladat: azonosító, műveleti idő, határidő (ugyanabban az időegységben, a tervezés kezdetétől mérve), érkezési sorszám, és ha kézi sorrendet is vizsgálsz, a kézi sorszám.",
        "2. A lap mind az öt sorolásra kiszámítja a befejezési időket, a pontatlanságot és a késedelmet, és összesíti: átlagos átfutás, késő feladatok száma, legnagyobb és teljes késedelem. A legördülő listában választott sorolás ütemtervét táblázat és időrács (Gantt-diagram) mutatja.",
        "3. A sorolási elvek: FCFS – érkezési sorrend; SPT – legrövidebb műveleti idő először (egy gépen az átlagos átfutást minimalizálja); EDD – legkorábbi határidő először (a legnagyobb késedelmet minimalizálja); CR – a határidőig hátralévő idő és a műveleti idő hányadosa szerint.",
        "4. A „Két gép (Johnson)” lapon minden feladat előbb az első, majd a második gépen halad át. A sablon a Johnson-sorrendet és az érkezési sorrendet ütemezi, kiszámítja a teljes átfutást és az alsó korlátot, és időrácson ábrázolja.",
        "5. Az időrács lépésközét a lap tetején állíthatod; a rács 40 cellás.",
        "■ Példa: a ForgácsTech megmunkáló központja és 3D mérőgépe (kézikönyv 21. fejezet).",
    ])
    ws = wb.create_sheet("Egy gép")
    cimsor(ws, "Egy gép: sorolási elvek összevetése")
    szoveg(ws["A3"], "Vizsgált sorolás (a Gantt-diagramhoz)", felkov=True); bemenet(ws["B3"], "EDD"); legordulo(ws, "B3", SZABALYOK)
    szoveg(ws["A4"], "A tervezés kezdete (CR-hez)", felkov=True); bemenet(ws["B4"], 0, "0.0")
    szoveg(ws["A5"], "Az időrács lépésköze", felkov=True); bemenet(ws["B5"], 1, "0.0")
    r1, rn = 9, 8 + N1
    fej = ["Azonosító", "Műveleti idő", "Határidő", "Érkezési sorszám", "Kézi sorszám"] + \
          [f"{sz} kulcs" for sz in SZABALYOK] + [f"{sz} rang" for sz in SZABALYOK] + \
          [f"{sz} befejezés" for sz in SZABALYOK] + [f"{sz} késedelem" for sz in SZABALYOK]
    R = lambda c: f"${c}${r1}:${c}${rn}"
    ures = lambda r: f'OR(A{r}="",N(B{r})<=0)'
    kulcs = {"FCFS": lambda r: f"N(D{r})+ROW()/1000000", "SPT": lambda r: f"B{r}+N(D{r})/10000+ROW()/1000000000",
             "EDD": lambda r: f"N(C{r})+N(D{r})/10000+ROW()/1000000000", "CR": lambda r: f"(N(C{r})-$B$4)/B{r}+N(D{r})/1000000+ROW()/1000000000",
             "kézi": lambda r: f"N(E{r})+N(D{r})/10000+ROW()/1000000000"}
    kepl = {}
    for j, sz in enumerate(SZABALYOK):
        kepl[6 + j] = (lambda r, sz=sz: f'=IF({ures(r)},1000000000,{kulcs[sz](r)})')
        kc = get_column_letter(6 + j)
        kepl[11 + j] = (lambda r, kc=kc: f'=IF({ures(r)},"",COUNTIF({R(kc)},"<"&{kc}{r})+1)')
        rk = get_column_letter(11 + j)
        kepl[16 + j] = (lambda r, rk=rk: f'=IF({rk}{r}="","",SUMIF({R(rk)},"<="&{rk}{r},{R("B")}))')
        bf = get_column_letter(16 + j)
        kepl[21 + j] = (lambda r, bf=bf: f'=IF({bf}{r}="","",MAX(0,{bf}{r}-N(C{r})))')
    sorok = [[a, p, d, i + 1, None] for i, (a, p, d) in enumerate(EGY)]
    for i in range(len(EGY), N1):
        sorok.append([None, None, None, i + 1, None])
    u = tablazat(ws, 8, fej, [11, 10, 10, 10, 10] + [9] * 5 + [7] * 5 + [10] * 5 + [10] * 5, sorok,
                 bemeneti_oszlopok=(1, 2, 3, 4, 5), kepletek=kepl,
                 formatumok={2: "0.0", 3: "0.0", **{c: '[>=1000000]"–";0.000' for c in range(6, 11)}})
    # hibás CR (osztás nullával) ellen: üres soroknál 999
    o0 = u + 2
    szoveg(ws.cell(row=o0, column=1), "Összesítés", felkov=True)
    fejlec(ws, o0 + 1, ["Mutató"] + SZABALYOK, None, oszlop=1)
    for j, (t, fn) in enumerate([("Átlagos átfutás", "AVERAGE"), ("Késő feladatok száma", "COUNTIF>0"),
                                  ("Legnagyobb késedelem", "MAX"), ("Teljes késedelem", "SUM")]):
        r = o0 + 2 + j
        szoveg(ws.cell(row=r, column=1), t)
        for k in range(5):
            if fn == "AVERAGE":
                rng = f"{get_column_letter(16 + k)}{r1}:{get_column_letter(16 + k)}{rn}"
                f = f'=IF(COUNT({rng})=0,"",AVERAGE({rng}))'
            else:
                rng = f"{get_column_letter(21 + k)}{r1}:{get_column_letter(21 + k)}{rn}"
                f = {"COUNTIF>0": f'=COUNTIF({rng},">0")', "MAX": f'=IF(COUNT({rng})=0,"",MAX({rng}))', "SUM": f"=SUM({rng})"}[fn]
            keplet(ws.cell(row=r, column=2 + k), f, "0.0" if fn != "COUNTIF>0" else "0", True)
    # a választott sorolás ütemterve
    s0 = o0 + 8
    szoveg(ws.cell(row=s0, column=1), "A választott sorolás ütemterve", felkov=True)
    fejlec(ws, s0 + 1, ["Hely", "Azonosító", "Kezdés", "Befejezés", "Határidő", "Késedelem"], None)
    oszl = 'MATCH($B$3,{"FCFS","SPT","EDD","CR","kézi"},0)'
    for k in range(N1):
        r = s0 + 2 + k
        szoveg(ws.cell(row=r, column=1), k + 1)
        rang = f"INDEX($K${r1}:$O${rn},0,{oszl})"
        keplet(ws.cell(row=r, column=2), f'=IFERROR(INDEX({R("A")},MATCH(A{r},{rang},0)),"")')
        keplet(ws.cell(row=r, column=4), f'=IF(B{r}="",1000000000,INDEX($P${r1}:$T${rn},MATCH(B{r},{R("A")},0),{oszl}))', '[>=1000000]"";0.0')
        keplet(ws.cell(row=r, column=3), f'=IF(B{r}="",1000000000,D{r}-INDEX({R("B")},MATCH(B{r},{R("A")},0)))', '[>=1000000]"";0.0')
        keplet(ws.cell(row=r, column=5), f'=IF(B{r}="","",INDEX({R("C")},MATCH(B{r},{R("A")},0)))', "0.0")
        keplet(ws.cell(row=r, column=6), f'=IF(B{r}="","",MAX(0,D{r}-E{r}))', "0.0")
    sl = s0 + 1 + N1
    g0 = sl + 2
    racs(ws, g0, "Gantt-diagram (időrács)", f"$B${s0 + 2}:$B${sl}", f"$C${s0 + 2}:$C${sl}", f"$D${s0 + 2}:$D${sl}", "$B$5")
    szoveg(ws.cell(row=g0 + 1, column=1), "A rács cellái a lépésköz egységeinek felelnek meg (az első cella 0-tól 1 lépésközig).")

    w2 = wb.create_sheet("Két gép (Johnson)")
    cimsor(w2, "Két gép egymás után: Johnson-eljárás")
    szoveg(w2["A3"], "Az időrács lépésköze", felkov=True); bemenet(w2["B3"], 1, "0.0")
    q1, qn = 7, 6 + N2
    Q = lambda c: f"${c}${q1}:${c}${qn}"
    fej = ["Azonosító", "1. gép ideje", "2. gép ideje", "Csoport", "Johnson-kulcs", "Johnson-hely", "Érkezési hely"]
    kepl = {4: lambda r: f'=IF(A{r}="","",IF(B{r}<=C{r},1,2))',
            5: lambda r: f'=IF(A{r}="","",IF(D{r}=1,B{r},1000000-C{r})+ROW()/1000000)',
            6: lambda r: f'=IF(A{r}="","",COUNTIF({Q("E")},"<"&E{r})+1)',
            7: lambda r: f'=IF(A{r}="","",COUNTA($A${q1}:A{r}))'}
    u2 = tablazat(w2, 6, fej, [11, 11, 11, 9, 12, 11, 11], [list(x) for x in KET], bemeneti_oszlopok=(1, 2, 3),
                  kepletek=kepl, uressor=N2 - len(KET), formatumok={2: "0.0", 3: "0.0", 5: "0.000000"})
    szoveg(w2.cell(row=u2 + 1, column=1), "1. csoport: az 1. gépi idő nem nagyobb a 2.-nál – elöl, az 1. gépi idő szerint növekvő sorrendben; 2. csoport: hátul, a 2. gépi idő szerint csökkenő sorrendben.")

    def utemterv(sor0, cim, helyoszlop):
        szoveg(w2.cell(row=sor0, column=1), cim, felkov=True)
        fejlec(w2, sor0 + 1, ["Hely", "Azonosító", "1. gép kezdés", "1. gép vége", "2. gép kezdés", "2. gép vége"], None)
        for k in range(N2):
            r = sor0 + 2 + k
            szoveg(w2.cell(row=r, column=1), k + 1)
            keplet(w2.cell(row=r, column=2), f'=IFERROR(INDEX({Q("A")},MATCH(A{r},{Q(helyoszlop)},0)),"")')
            elozo1 = "0" if k == 0 else f"D{r - 1}"
            elozo2 = "0" if k == 0 else f"F{r - 1}"
            keplet(w2.cell(row=r, column=3), f'=IF(B{r}="",1000000000,{elozo1})', '[>=1000000]"";0.0')
            keplet(w2.cell(row=r, column=4), f'=IF(B{r}="",{elozo1},C{r}+INDEX({Q("B")},MATCH(B{r},{Q("A")},0)))', "0.0")
            keplet(w2.cell(row=r, column=5), f'=IF(B{r}="",1000000000,MAX(D{r},{elozo2}))', '[>=1000000]"";0.0')
            keplet(w2.cell(row=r, column=6), f'=IF(B{r}="",{elozo2},E{r}+INDEX({Q("C")},MATCH(B{r},{Q("A")},0)))', "0.0")
        return sor0 + 1 + N2
    j0 = u2 + 3
    jl = utemterv(j0, "Johnson-sorrend", "F")
    f0 = jl + 2
    fl = utemterv(f0, "Érkezési sorrend", "G")
    e0 = fl + 2
    szoveg(w2.cell(row=e0, column=1), "Eredmények", felkov=True)
    for k, (t, f) in enumerate([("Teljes átfutás, Johnson-sorrend", f"=MAX(F{j0 + 2}:F{jl})"),
                                ("Teljes átfutás, érkezési sorrend", f"=MAX(F{f0 + 2}:F{fl})"),
                                ("Alsó korlát", f'=IF(COUNT({Q("B")})=0,"",MAX(SUM({Q("B")})+MIN({Q("C")}),SUM({Q("C")})+MIN({Q("B")})))'),
                                ("Megtakarítás a Johnson-sorrenddel", f"=B{e0 + 2}-B{e0 + 1}")]):
        szoveg(w2.cell(row=e0 + 1 + k, column=1), t)
        keplet(w2.cell(row=e0 + 1 + k, column=2), f, "0.0", True)
    w2.column_dimensions["A"].width = 34
    g = e0 + 7
    racs(w2, g, "Johnson: 1. gép", f"$B${j0 + 2}:$B${jl}", f"$C${j0 + 2}:$C${jl}", f"$D${j0 + 2}:$D${jl}", "$B$3")
    racs(w2, g + 1, "Johnson: 2. gép", f"$B${j0 + 2}:$B${jl}", f"$E${j0 + 2}:$E${jl}", f"$F${j0 + 2}:$F${jl}", "$B$3")
    racs(w2, g + 3, "Érkezési: 1. gép", f"$B${f0 + 2}:$B${fl}", f"$C${f0 + 2}:$C${fl}", f"$D${f0 + 2}:$D${fl}", "$B$3")
    racs(w2, g + 4, "Érkezési: 2. gép", f"$B${f0 + 2}:$B${fl}", f"$E${f0 + 2}:$E${fl}", f"$F${f0 + 2}:$F${fl}", "$B$3")
    return mentes(wb, "gantt_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
