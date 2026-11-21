"""Ok-okozati (halszálka-) diagram és 5 miért (eszközlap: Ok-okozati diagram)."""
from openpyxl.formatting.rule import FormulaRule

from _kozos import *  # noqa: F401,F403

KATEG = ["módszer", "anyag", "ember", "gép", "mérés", "környezet"]
NO, NK = 40, 8

PROBLEMA = "Anyagra várás a megmunkáló gépeknél (havi 1120 perc, az állásidő 31%-a)"
OKOK = [
    ("módszer", "anyagkiadás csak a műszak elején", "a raktári rend így alakult ki", 6, "igazolt", "MES-napló: a várakozások 64%-a átsorolás után", "logisztikai vezető"),
    ("módszer", "az anyagigény nem az ütemtervből jön", "a raktár a heti listából dolgozik", 5, "igazolt", "a raktári kiadások 80%-a a heti lista szerint", "logisztikai vezető"),
    ("módszer", "átsorolás anyagellenőrzés nélkül", "az ütemező nem látja a készletet", 7, "igazolt", "MES-napló: 17 átsorolásból 11 után várakozás", "termelésvezető"),
    ("anyag", "hiányzó rúdanyag (A-tételek)", "a rendelési pont túl alacsony", 4, "igazolt", "a várakozások 11%-a anyaghiány miatt", "beszerző"),
    ("anyag", "hibás méretű szállítmány", "", 1, "elvetett", "három hónap alatt egy eset", "minőségügy"),
    ("ember", "egy raktáros műszakonként", "", 3, "vizsgálandó", "", "logisztikai vezető"),
    ("ember", "a kezelő nem jelez előre", "nincs rá eszköz", 2, "vizsgálandó", "", "műszakvezető"),
    ("gép", "a darabolás (fűrészgép) szűk keresztmetszet", "", 3, "elvetett", "a fűrészgép kihasználtsága 52%", "karbantartás"),
    ("gép", "kevés targonca", "", 2, "elvetett", "a targonca a várakozások idején szabad volt", "logisztikai vezető"),
    ("mérés", "a készletnyilvántartás nem valós idejű", "a kiadást műszak végén rögzítik", 4, "igazolt", "leltáreltérés a rúdanyagoknál 6%", "kontroller"),
    ("környezet", "a raktár távol van a csarnoktól", "", 1, "elvetett", "az út 4 perc, a várakozás átlagosan 29 perc", "logisztikai vezető"),
    ("környezet", "kevés átmeneti tárolóhely", "", 2, "vizsgálandó", "", "termelésvezető"),
]

MIERT = [
    ("Miért vár a gép anyagra?", "Mert az átsorolt rendelés anyaga nincs kikészítve.", "MES-napló, 26 eset"),
    ("Miért nincs kikészítve?", "Mert az anyagot csak a műszak elején, az akkori sorrend szerint adják ki.", "raktári kiadási napló"),
    ("Miért csak a műszak elején?", "Mert a raktáros a műszak elején kapja meg a listát, közben nem kap értesítést.", "interjú a raktárossal"),
    ("Miért nem kap értesítést?", "Mert a MES ütemezője átsoroláskor nem küld anyagigényt a raktárnak.", "a MES konfigurációja"),
    ("Miért nem küld?", "Mert az anyagkiadás nem volt része a bevezetett folyamatnak (a BPMN-modellben sem szerepelt).", "a jövőbeli BPMN-modell"),
]


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Ok-okozati (halszálka-) diagram – sablon", [
        "■ Mire való? Egy probléma lehetséges okainak rendszerezése okcsoportok szerint, a csapat értékelésének (szavazatok) rögzítése, "
        "és annak nyilvántartása, mely okokat igazoltak vagy vetettek el adatokkal.",
        "■ Okok: a B4 cellába írd a problémát (hatást) mérhető formában. Egy sor egy lehetséges ok: okcsoport, ok, mélyebb ok "
        "(miért?), a csapat szavazatai, az igazolás állapota és a bizonyíték. Legfeljebb 40 ok.",
        "■ Az okcsoportok alapértelmezésben: módszer, anyag, ember, gép, mérés, környezet; a Csoportok lapon átírhatók (legfeljebb 8).",
        "■ Diagram: az okok csoportonként, halszálka-elrendezésben (automatikus). A rajzolt diagramot a notebook készíti el.",
        "■ 5 miért: a legvalószínűbb ok mélyebb okainak feltárása egymást követő miért-kérdésekkel, bizonyítékkal.",
        "■ Fontos: a diagram lehetséges okokat gyűjt. Gyökérok csak az az ok lehet, amelyet adatokkal igazoltak.",
        "A kitöltött példa a ForgácsTech anyagra várási problémája (kézikönyv 25. fejezet).",
        "Források: Ishikawa: Guide to Quality Control (1982); Montgomery (2020); NASA RP-1358 (1994), 7.2. szakasz.",
    ])

    # ---- Csoportok
    wc = wb.create_sheet("Csoportok")
    cimsor(wc, "Okcsoportok", "Legfeljebb 8 csoport; az első hat a diagramon jelenik meg (három fent, három lent).")
    tablazat(wc, 4, ["Okcsoport"], [22], [[k] for k in KATEG], bemeneti_oszlopok=(1,), uressor=NK - len(KATEG))
    CS = "'Csoportok'!$A$5:$A$12"

    # ---- Okok
    ws = wb.create_sheet("Okok")
    cimsor(ws, "Lehetséges okok")
    szoveg(ws["A4"], "Probléma (hatás):", felkov=True)
    bemenet(ws["B4"], PROBLEMA)
    ws.merge_cells("B4:G4")
    fej = ["Okcsoport", "Lehetséges ok", "Mélyebb ok (miért?)", "Szavazat", "Igazolás", "Bizonyíték, adat", "Felelős", "Sorszám a csoportban", "Kulcs"]
    ut = tablazat(ws, 5, fej, [14, 36, 30, 9, 13, 42, 18, 10, 18], [list(o) for o in OKOK],
                  bemeneti_oszlopok=tuple(range(1, 8)),
                  kepletek={8: lambda r: f'=IF(OR(A{r}="",B{r}=""),"",COUNTIFS($A$6:A{r},A{r},$B$6:B{r},"<>"))',
                            9: lambda r: f'=IF(H{r}="","",A{r}&"|"&H{r})'},
                  uressor=NO - len(OKOK), formatumok={4: "0"})
    from openpyxl.worksheet.datavalidation import DataValidation
    dv = DataValidation(type="list", formula1=f"={CS}", allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"A6:A{ut}")
    legordulo(ws, f"E6:E{ut}", ["vizsgálandó", "igazolt", "elvetett"])
    ws.conditional_formatting.add(f"E6:E{ut}", FormulaRule(formula=['E6="igazolt"'], fill=PatternFill("solid", fgColor="DDEFE4")))
    ws.conditional_formatting.add(f"E6:E{ut}", FormulaRule(formula=['E6="elvetett"'], fill=PatternFill("solid", fgColor="F1F2F4")))
    ws.freeze_panes = "B6"
    O_UT = ut

    # ---- Összesítés
    wo = wb.create_sheet("Összesítés")
    cimsor(wo, "Összesítés okcsoportonként")
    fejlec(wo, 4, ["Okcsoport", "Okok", "Szavazat", "Igazolt", "Vizsgálandó", "Elvetett"], [22, 9, 10, 10, 12, 10])
    A, D_, E_ = f"'Okok'!$A$6:$A${O_UT}", f"'Okok'!$D$6:$D${O_UT}", f"'Okok'!$E$6:$E${O_UT}"
    for i in range(NK):
        r = 5 + i
        keplet(wo.cell(row=r, column=1), f"=IF('Csoportok'!A{5 + i}=\"\",\"\",'Csoportok'!A{5 + i})")
        keplet(wo.cell(row=r, column=2), f'=IF(A{r}="","",COUNTIF({A},A{r}))', "0")
        keplet(wo.cell(row=r, column=3), f'=IF(A{r}="","",SUMIF({A},A{r},{D_}))', "0")
        for j, al in enumerate(["igazolt", "vizsgálandó", "elvetett"]):
            keplet(wo.cell(row=r, column=4 + j), f'=IF(A{r}="","",COUNTIFS({A},A{r},{E_},"{al}"))', "0")
    rt = 5 + NK
    szoveg(wo.cell(row=rt, column=1), "Összesen", felkov=True)
    for k in range(2, 7):
        cl = get_column_letter(k)
        keplet(wo.cell(row=rt, column=k), f"=SUM({cl}5:{cl}{rt - 1})", "0", True)
    ch = BarChart()
    ch.type, ch.grouping, ch.overlap = "bar", "stacked", 100
    diagram_kozos(ch, "Okok az igazolás állapota szerint", None, "okok száma", 18, 8)
    ch.add_data(Reference(wo, min_col=4, max_col=6, min_row=4, max_row=4 + len(KATEG)), titles_from_data=True)
    ch.set_categories(Reference(wo, min_col=1, min_row=5, max_row=4 + len(KATEG)))
    wo.add_chart(ch, "H4")

    # ---- Diagram (cellás halszálka-elrendezés)
    wd = wb.create_sheet("Diagram")
    cimsor(wd, "Halszálka-elrendezés", "Az okok csoportonként (automatikus). Zöld: igazolt ok.")
    for k in range(1, 8):
        wd.column_dimensions[get_column_letter(k)].width = 34 if k in (1, 3, 5) else 3
    wd.column_dimensions["G"].width = 30
    K = f"'Okok'!$I$6:$I${O_UT}"
    B_ = f"'Okok'!$B$6:$B${O_UT}"
    for blokk, (sor0, csoportok) in enumerate([(4, [0, 1, 2]), (16, [3, 4, 5])]):
        for j, ci in enumerate(csoportok):
            col = 1 + 2 * j
            c = wd.cell(row=sor0, column=col, value=f"=IF('Csoportok'!A{5 + ci}=\"\",\"\",'Csoportok'!A{5 + ci})")
            c.font, c.fill, c.alignment, c.border = fej_font, fej_fill, kozep, keret
            for k in range(1, 9):
                cc = wd.cell(row=sor0 + k, column=col)
                cc.value = (f"=IFERROR(INDEX({B_},MATCH({get_column_letter(col)}${sor0}&\"|\"&{k},{K},0)),\"\")")
                cc.font, cc.border, cc.alignment = alap_font, keret, tord
            wd.conditional_formatting.add(
                f"{get_column_letter(col)}{sor0 + 1}:{get_column_letter(col)}{sor0 + 8}",
                FormulaRule(formula=[f"COUNTIFS({B_},{get_column_letter(col)}{sor0 + 1},'Okok'!$E$6:$E${O_UT},\"igazolt\")>0"],
                            fill=PatternFill("solid", fgColor="DDEFE4")))
    for c_ in range(1, 7):
        x = wd.cell(row=14, column=c_, value="→" if c_ == 6 else "———")
        x.font, x.alignment = Font(name=BETU, size=14, bold=True, color=KEK), kozep
    p = wd.cell(row=14, column=7, value="='Okok'!B4")
    p.font, p.fill, p.alignment, p.border = felkover, PatternFill("solid", fgColor="FBE7D9"), tord, keret
    wd.row_dimensions[14].height = 48

    # ---- 5 miért
    wm = wb.create_sheet("5 miért")
    cimsor(wm, "5 miért", "Addig kérdezz, amíg olyan okhoz nem érsz, amelyre intézkedés tervezhető; minden választ igazolj.")
    tablazat(wm, 4, ["Lépés", "Kérdés", "Válasz", "Bizonyíték"], [7, 34, 60, 28],
             [[i + 1, *m] for i, m in enumerate(MIERT)], bemeneti_oszlopok=(2, 3, 4), uressor=2)
    szoveg(wm["A13"], "Gyökérok:", felkov=True)
    bemenet(wm["B13"], "Az anyagkiadás folyamata nincs összekötve az ütemezéssel; az átsorolás nem vált ki anyagigényt.")
    wm.merge_cells("B13:D13")
    szoveg(wm["A14"], "Intézkedés:", felkov=True)
    bemenet(wm["B14"], "Átsoroláskor a MES ellenőrzi az anyagot és anyagigényt küld; anyagkiadás kétóránként az ütemterv alapján.")
    wm.merge_cells("B14:D14")
    return mentes(wb, "halszalka_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
