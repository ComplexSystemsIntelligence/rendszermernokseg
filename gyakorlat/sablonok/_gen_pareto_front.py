"""Dominanciavizsgálat és Pareto-front két célra (eszközlap: Pareto-front)."""
import json

from _kozos import *  # noqa: F401,F403

D = json.loads((MAPPA.parents[1] / "_shared" / "adat" / "pareto_bringa.json").read_text(encoding="utf-8"))
NV = 20


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Pareto-front – sablon", [
        "■ Mire való? Tervváltozatok szűkítése súlyok nélkül: a dominált változatok kiszűrése és a nem dominált változatok (a közelítő Pareto-front) azonosítása két cél szerint.",
        "1. A „Változatok” lapon add meg a két cél nevét és irányát (min vagy max), majd soronként a változatok kódját, leírását és a két cél értékét.",
        "2. Egy változat akkor dominál egy másikat, ha mindkét cél szerint legalább olyan jó, és legalább az egyik szerint jobb. A „Dominancia” lap ezt minden párra kiszámolja.",
        "3. A sorösszeg megmutatja, hány változatot dominál az adott változat; az oszlopösszeg azt, hány változat dominálja. A nem dominált változatok oszlopösszege 0.",
        "4. Ha van korlát (például költségkeret), add meg: a lap kiválasztja a korlátot teljesítő nem dominált változatok közül a másik cél szerint legjobbat.",
        "5. Több cél és nagy változatszám esetén használd a pareto_front notebookot.",
        "■ Példa: a VárosiBringa tizenkét tervváltozata (kézikönyv 10. fejezet).",
    ])
    vs = wb.create_sheet("Változatok")
    cimsor(vs, "Tervváltozatok")
    for r, (t, v) in enumerate([("1. cél neve", "éves költség [MFt/év]"), ("1. cél iránya", "min"),
                                ("2. cél neve", "elérhetőség [%]"), ("2. cél iránya", "max"),
                                ("Korlát az 1. célra (üres = nincs)", 80)], start=3):
        szoveg(vs.cell(row=r, column=1), t, felkov=True)
        bemenet(vs.cell(row=r, column=2), v)
    legordulo(vs, "B4", ["min", "max"])
    legordulo(vs, "B6", ["min", "max"])
    vs.column_dimensions["A"].width = 30
    sor = [[v["kod"], f"{v['kerekpar']} kerékpár, {v['dokkolo']} dokkoló, {v['furgon']} furgon", v["koltseg"], v["elerhetoseg"]]
           for v in D["valtozatok"]]
    R0 = 10
    kepl = {5: lambda r: f'=IF(A{r}="","",IF(INDEX(Dominancia!$B${R0 + NV + 1}:${get_column_letter(1 + NV)}${R0 + NV + 1},1,ROW()-{R0})=0,"nem dominált","dominált"))',
            6: lambda r: f'=IF(A{r}="","",INDEX(Dominancia!${get_column_letter(2 + NV)}${R0 + 1}:${get_column_letter(2 + NV)}${R0 + NV},ROW()-{R0}))',
            7: lambda r: f'=IF(OR(A{r}="",E{r}<>"nem dominált"),"",IF($B$7="","igen",IF(IF($B$4="min",C{r}<=$B$7,C{r}>=$B$7),"igen","nem")))',
            8: lambda r: f'=IF(G{r}="igen",D{r},"")'}
    u = tablazat(vs, R0, ["Kód", "Leírás", "1. cél", "2. cél", "Állapot", "Hány változatot dominál", "Teljesíti a korlátot?", "2. cél, ha jelölt (segéd)"],
                 [10, 36, 14, 14, 16, 14, 14, 14], sor, bemeneti_oszlopok=(1, 2, 3, 4), kepletek=kepl, uressor=NV - len(sor))
    keplet(vs.cell(row=R0, column=3), "=B3")
    keplet(vs.cell(row=R0, column=4), "=B5")
    for c in (3, 4):
        vs.cell(row=R0, column=c).fill, vs.cell(row=R0, column=c).font = fej_fill, fej_font
    rr = u + 2
    szoveg(vs.cell(row=rr, column=2), "Nem dominált változatok száma", felkov=True)
    keplet(vs.cell(row=rr, column=3), f'=COUNTIF(E{R0 + 1}:E{u},"nem dominált")', felkov=True)
    szoveg(vs.cell(row=rr + 1, column=2), "Legjobb a korláton belül (2. cél szerint)", felkov=True)
    keplet(vs.cell(row=rr + 1, column=3),
           f'=IFERROR(INDEX(A{R0 + 1}:A{u},MATCH(IF($B$6="max",_xlfn.MAXIFS(D{R0 + 1}:D{u},G{R0 + 1}:G{u},"igen"),_xlfn.MINIFS(D{R0 + 1}:D{u},G{R0 + 1}:G{u},"igen")),'
           f'H{R0 + 1}:H{u},0)),"nincs ilyen")', felkov=True)
    ch = ScatterChart()
    ser = Series(Reference(vs, min_col=4, min_row=R0 + 1, max_row=R0 + len(sor)),
                 Reference(vs, min_col=3, min_row=R0 + 1, max_row=R0 + len(sor)), title="változatok")
    ser.marker.symbol = "circle"
    ser.marker.size = 7
    ser.graphicalProperties.line.noFill = True
    ch.series.append(ser)
    diagram_kozos(ch, "Változatok a két cél síkján", "1. cél", "2. cél", 16, 9)
    ch.legend = None
    vs.add_chart(ch, f"J{R0}")

    dm = wb.create_sheet("Dominancia")
    cimsor(dm, "Dominanciamátrix", "1 = a sor változata dominálja az oszlop változatát.")
    dm.column_dimensions["A"].width = 10
    for j in range(NV):
        c = dm.cell(row=R0, column=2 + j)
        keplet(c, f'=IF(Változatok!A{R0 + 1 + j}="","",Változatok!A{R0 + 1 + j})')
        c.fill, c.font, c.alignment = fej_fill, fej_font, kozep
        dm.column_dimensions[get_column_letter(2 + j)].width = 5
        keplet(dm.cell(row=R0 + 1 + j, column=1), f'=IF(Változatok!A{R0 + 1 + j}="","",Változatok!A{R0 + 1 + j})')
    for i in range(NV):
        ri = R0 + 1 + i
        for j in range(NV):
            rj = R0 + 1 + j
            a1, b1 = f"Változatok!$C${ri}", f"Változatok!$C${rj}"
            a2, b2 = f"Változatok!$D${ri}", f"Változatok!$D${rj}"
            s1 = 'IF(Változatok!$B$4="min",-1,1)'
            s2 = 'IF(Változatok!$B$6="min",-1,1)'
            f = (f'=IF(OR({i}={j},Változatok!$A${ri}="",Változatok!$A${rj}=""),0,'
                 f'IF(AND({s1}*{a1}>={s1}*{b1},{s2}*{a2}>={s2}*{b2},OR({s1}*{a1}>{s1}*{b1},{s2}*{a2}>{s2}*{b2})),1,0))')
            c = dm.cell(row=ri, column=2 + j)
            keplet(c, f)
            c.alignment = kozep
        keplet(dm.cell(row=ri, column=2 + NV), f"=SUM(B{ri}:{get_column_letter(1 + NV)}{ri})")
    fejlec(dm, R0, ["Σ dominál"], [10], oszlop=2 + NV)
    szoveg(dm.cell(row=R0 + NV + 1, column=1), "Σ dominálja", felkov=True)
    for j in range(NV):
        col = get_column_letter(2 + j)
        keplet(dm.cell(row=R0 + NV + 1, column=2 + j), f"=SUM({col}{R0 + 1}:{col}{R0 + NV})")
    return mentes(wb, "pareto_front_sablon.xlsx")
