"""Ötletroham, 6-3-5, névleges csoporttechnika és Delphi (eszközlap: Ötletroham és társai)."""
from _kozos import *  # noqa: F401,F403

OTLETEK = [
    ("sürgős rendelések szóbeli előresorolása", "ütemezés"), ("alapanyag-beérkezés bizonytalansága", "beszerzés"),
    ("váratlan gépleállások", "gépállapot"), ("hosszú beállítási idők", "gépállapot"), ("hiányos műszakátadás", "információ"),
    ("a gépállapot csak a műszak végén ismert", "információ"), ("szerszámhiány", "erőforrás"), ("NC-program késése", "technológia"),
    ("minőségi visszatartás", "minőség"), ("túl optimista szállítási ígéret", "értékesítés"), ("kapacitásnaptár nem naprakész", "ütemezés"),
    ("betegség miatti hiányzás", "erőforrás"),
]
# NGT: 11 résztvevő, mindenki 5 ötletet pontoz (5 = legfontosabb)
NGT = [
    [5, 4, 5, 3, 5, 4, 5, 5, 4, 3, 5], [4, 5, 3, 5, 4, 3, 4, None, 5, 4, 3], [3, None, 4, 4, 3, 5, 2, 4, None, 5, 4],
    [None, 3, None, None, 2, None, 3, 3, 3, None, None], [2, None, None, 2, None, 2, None, 2, None, 2, 2],
    [None, 2, 2, None, None, None, None, None, 2, None, None], [1, None, None, 1, None, None, 1, None, None, 1, None],
    [None, 1, None, None, 1, None, None, None, None, None, 1], [None, None, 1, None, None, 1, None, None, 1, None, None],
    [None, None, None, None, None, None, None, 1, None, None, None], [None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None],
]
DELPHI = [  # szakértő: 1., 2., 3. kör becslése (hét)
    ("1. szakértő", 6, 8, 8), ("2. szakértő", 12, 10, 9), ("3. szakértő", 8, 8, 8), ("4. szakértő", 20, 14, 11),
    ("5. szakértő", 10, 9, 9), ("6. szakértő", 7, 8, 8), ("7. szakértő", 9, 9, 9),
]


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Ötletroham, 6-3-5, névleges csoport, Delphi – sablon", [
        "■ Mire való? Csoportos ötletgyűjtés (ötletroham, 6-3-5 ötletírás), az ötletek csendes rangsorolása (névleges csoporttechnika) és szakértői becslés több körben (Delphi).",
        "1. A „6-3-5” lapon hat résztvevő lapja hat körön át: körönként mindenki három ötletet ír a kapott lapra, a korábbiakra építve. Legfeljebb 108 ötlet.",
        "2. Az „Ötletlista” lapra gyűjtsd össze az ötleteket (bármelyik módszerből), és sorold be őket működési elv vagy kategória szerint. A lap kiszámolja a mennyiséget és a változatosságot (különböző kategóriák száma).",
        "3. A „Névleges csoport” lapon minden résztvevő csendben pontozza a legfontosabb öt ötletet (5 = legfontosabb, 1 = ötödik). A lap összesíti a pontokat, a szavazatok számát és a rangsort.",
        "4. A „Delphi” lapon szakértőnként és körönként rögzítsd a becsléseket. A lap körönként kiszámolja a mediánt és az interkvartilis terjedelmet: a terjedelem csökkenése a konszenzus felé haladást mutatja.",
        "■ Példa: a ForgácsTech késési okainak gyűjtése és rangsorolása, valamint az ütemezőmodul bevezetési idejének Delphi-becslése.",
    ])
    s = wb.create_sheet("6-3-5")
    cimsor(s, "6-3-5 ötletírás", "Lap = résztvevő lapja; kör = 5 perc; minden körben 3 új ötlet a lapra.")
    sorok = []
    for lap in range(1, 7):
        for kor in range(1, 7):
            sorok.append([lap, kor, None, None, None])
    sorok[0][2:] = ["ütemező tábla a műhelyben", "napi 10 perces eltérés-egyeztetés", "gépállapot automatikus gyűjtése"]
    sorok[1][2:] = ["eltérés esetén automatikus értesítés", "a táblát a MES frissítse", "átsorolás csak jóváhagyással"]
    u = tablazat(s, 4, ["Lap", "Kör", "1. ötlet", "2. ötlet", "3. ötlet"], [7, 7, 40, 40, 40], sorok, bemeneti_oszlopok=(3, 4, 5))
    szoveg(s.cell(row=u + 2, column=3), "Ötletek száma", felkov=True)
    keplet(s.cell(row=u + 2, column=4), f"=COUNTA(C5:E{u})", felkov=True)
    ol = wb.create_sheet("Ötletlista")
    cimsor(ol, "Ötletlista", "Kategória: működési elv vagy témakör. Újdonság: 1 = szokásos, 2 = kevésbé szokásos, 3 = újszerű.")
    sor = [[i + 1, o, k, "névleges csoport", None, None] for i, (o, k) in enumerate(OTLETEK)]
    u = tablazat(ol, 4, ["Sorszám", "Ötlet", "Kategória", "Forrás (módszer)", "Ismétlés? (igen/nem)", "Újdonság (1–3)"],
                 [9, 44, 18, 18, 14, 12], sor, bemeneti_oszlopok=range(2, 7), uressor=60)
    legordulo(ol, f"E5:E{u}", ["igen", "nem"])
    r0 = u + 2
    for k_, (t, f) in enumerate([
            ("Ötletek száma (mennyiség)", f'=COUNTIF(B5:B{u},"?*")'),
            ("Ismétlések", f'=COUNTIF(E5:E{u},"igen")'),
            ("Különböző kategóriák (változatosság)", f'=SUMPRODUCT((C5:C{u}<>"")/COUNTIF(C5:C{u},C5:C{u}&""))'),
            ("Újszerű (3-as) ötletek aránya", f'=IF(COUNT(F5:F{u})=0,"",COUNTIF(F5:F{u},3)/COUNT(F5:F{u}))')]):
        szoveg(ol.cell(row=r0 + k_, column=2), t, felkov=True)
        keplet(ol.cell(row=r0 + k_, column=3), f, "0%" if "arány" in t else "0")
    ng = wb.create_sheet("Névleges csoport")
    cimsor(ng, "Névleges csoporttechnika: csendes pontozás", "Mindenki az általa legfontosabbnak tartott öt ötletet pontozza: 5, 4, 3, 2, 1.")
    NP_ = 11
    fej = ["Ötlet"] + [f"R{j + 1}" for j in range(NP_)] + ["Pontszám", "Szavazatok", "Rang"]
    sor = [[o] + NGT[i] for i, (o, _) in enumerate(OTLETEK)]
    kepl = {NP_ + 2: lambda r: f'=IF(A{r}="","",SUM(B{r}:{get_column_letter(1 + NP_)}{r}))',
            NP_ + 3: lambda r: f'=IF(A{r}="","",COUNT(B{r}:{get_column_letter(1 + NP_)}{r}))',
            NP_ + 4: lambda r: f'=IF(A{r}="","",RANK({get_column_letter(NP_ + 2)}{r},${get_column_letter(NP_ + 2)}$5:${get_column_letter(NP_ + 2)}$34)+COUNTIFS(${get_column_letter(NP_ + 2)}$5:{get_column_letter(NP_ + 2)}{r},{get_column_letter(NP_ + 2)}{r})-1)'}
    u = tablazat(ng, 4, fej, [40] + [5] * NP_ + [10, 10, 7], sor, bemeneti_oszlopok=range(1, NP_ + 2), kepletek=kepl,
                 uressor=30 - len(sor))
    for r in range(5, u + 1):
        for j in range(NP_):
            ng.cell(row=r, column=2 + j).alignment = kozep
    megjegyzes(ng.cell(row=4, column=NP_ + 4), "Holtversenynél a táblázatban előrébb álló ötlet kapja a jobb rangot.")
    de = wb.create_sheet("Delphi")
    cimsor(de, "Delphi-becslés", "Kérdés: hány hét alatt vezethető be az ütemezőmodul a műhely minden gépén?")
    u = tablazat(de, 4, ["Szakértő", "1. kör", "2. kör", "3. kör", "4. kör"], [16, 10, 10, 10, 10],
                 [list(x) + [None] for x in DELPHI], bemeneti_oszlopok=range(1, 6), uressor=13 - len(DELPHI),
                 formatumok={2: "0.0", 3: "0.0", 4: "0.0", 5: "0.0"})
    stat = [("Válaszok száma", "COUNT"), ("Medián", "MEDIAN"), ("Alsó kvartilis (Q1)", "Q1"), ("Felső kvartilis (Q3)", "Q3"),
            ("Interkvartilis terjedelem", "IQR"), ("Terjedelem / medián", "REL")]
    r0 = u + 2
    for k_, (t, f) in enumerate(stat):
        szoveg(de.cell(row=r0 + k_, column=1), t, felkov=True)
        for j in range(4):
            col = get_column_letter(2 + j)
            rg = f"{col}5:{col}{u}"
            if f == "COUNT":
                v = f"=COUNT({rg})"
            elif f == "MEDIAN":
                v = f'=IF(COUNT({rg})=0,"",MEDIAN({rg}))'
            elif f == "Q1":
                v = f'=IF(COUNT({rg})=0,"",QUARTILE({rg},1))'
            elif f == "Q3":
                v = f'=IF(COUNT({rg})=0,"",QUARTILE({rg},3))'
            elif f == "IQR":
                v = f'=IF(COUNT({rg})=0,"",{col}{r0 + 3}-{col}{r0 + 2})'
            else:
                v = f'=IF(COUNT({rg})=0,"",{col}{r0 + 4}/{col}{r0 + 1})'
            keplet(de.cell(row=r0 + k_, column=2 + j), v, "0%" if f == "REL" else "0.0")
    megjegyzes(de.cell(row=r0 + 5, column=1), "Gyakorlati konszenzusjel: a relatív interkvartilis terjedelem körről körre csökken, és egy előre rögzített határ (például 20%) alá kerül.")
    return mentes(wb, "otletroham_sablon.xlsx")
