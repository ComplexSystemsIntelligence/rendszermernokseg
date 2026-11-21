"""Követelmény-verifikációs mátrix (eszközlap: Követelmény-verifikációs mátrix)."""
from openpyxl.formatting.rule import FormulaRule

from _kozos import *  # noqa: F401,F403

NR, NE, NM = 40, 20, 50
MODOK = ["vizsgálat", "elemzés", "bemutatás", "teszt", "elemzés és teszt", "elemzés és bemutatás"]
ALLAPOTOK = ["tervezett", "folyamatban", "teljesült", "nem teljesült", "eltérési engedély"]

MATRIX = [
    ("R-01", "SyRS 3.1", "A cellának egy motort legfeljebb 75 s alatt kell összeszerelnie.",
     "A háromműszakos próbaüzem műszakátlagaiból számolt átlag 95%-os egyoldali felső konfidenciahatára ≤ 75 s.",
     "elemzés és teszt", "rendszer", "SAT (előtte FAT)", "igen", "rendszermérnök", "VE-01", "SAT-jegyzőkönyv 4.2", "teljesült", "E-01"),
    ("R-02", "SyRS 3.4", "A cella havi rendelkezésre állásának el kell érnie a 95%-ot.",
     "A megbízhatósági blokkdiagram és a tervezett állásidők alapján ≥ 95%; az üzemi adatok az első három hónapban megerősítendők.",
     "elemzés", "rendszer", "tervezés", "nem", "rendszermérnök", "VE-02", "Megbízhatósági elemzés 2. vált.", "teljesült", None),
    ("R-03", "SyRS 3.2", "A cellának a nyolc csavart 4,0 ± 0,2 Nm nyomatékkal kell meghúznia.",
     "A próbaüzem minden kötése a tűrésmezőn belül; legalább 2302 kötés hiba nélkül (R ≥ 0,999, C = 90%).",
     "teszt", "alrendszer", "FAT és SAT", "igen", "minőségügy", "VE-03", "SAT-jegyzőkönyv 4.3", "teljesült", "E-03"),
    ("R-05", "SyRS 5.1", "A munkaasztalon végzett minden műveletnek legfeljebb 20°-os törzshajlítással elvégezhetőnek kell lennie.",
     "Digitális emberi modell az 5. és a 95. percentilisre ≤ 20°; próba három kezelővel.",
     "elemzés és bemutatás", "rendszer", "FAT", "nem", "ergonómus", "VE-05", "Ergonómiai jelentés", "teljesült", None),
    ("R-07", "SyRS 3.3", "Ha egy csavar nyomatéka a tűrésen kívül esik, akkor a cellának a motort hibásként kell megjelölnie.",
     "20 szándékosan hibás kötésből (hiányzó, laza csavar) mind hibásként jelölve.",
     "teszt", "rendszer", "FAT", "igen", "robotintegrátor", "VE-07", "FAT-jegyzőkönyv 3.5", "teljesült", None),
    ("R-09", "SyRS 4.2", "A cellának minden kész motor nyomatékadatait a motor azonosítójához rendelve kell a MES-nek átadnia.",
     "10 motor adatai a MES-ben a motor azonosítójához rendelve, egyezésben a csavarozó vezérlő naplójával.",
     "bemutatás", "rendszer", "FAT", "igen", "informatika", "VE-09", "FAT-jegyzőkönyv 3.8", "teljesült", "E-02"),
    ("R-11", "SyRS 6.1", "Amíg személy tartózkodik a védőzónában, a kobot sebességének legfeljebb 250 mm/s-nak kell lennie.",
     "Sebességmérés három pozícióban, próbatesttel a védőzónában; minden mért érték ≤ 250 mm/s.",
     "teszt", "rendszer", "FAT", "igen", "munkavédelem", "VE-11", "FAT-jegyzőkönyv 2.1", "teljesült", None),
    ("R-12", "SyRS 5.3", "A típusváltást egy betanított kezelőnek legfeljebb 10 perc alatt el kell tudnia végezni.",
     "Három kezelő, mindegyik két típusváltás; mind ≤ 10 perc, segítség nélkül.",
     "bemutatás", "rendszer", "SAT", "nem", "gyártástechnológus", "VE-12", None, "folyamatban", None),
    ("R-15", "SyRS 7.1", "A cellának el kell férnie a jelenlegi 6 × 4 m-es területen.",
     "Helyszíni felmérés és elrendezési rajz; a cella a kijelölt területen belül.",
     "vizsgálat", "rendszer", "telepítés", "nem", "karbantartás", "VE-15", "Elrendezési rajz C-102", "teljesült", None),
]

ELTERESEK = [
    ("E-01", "R-01", "FAT", "A ciklusidő 77,4 s, a követelmény 75 s.", "termékhiba",
     "Az idődiagram szerint a kobot a csavarozás után feleslegesen visszatér a nyugalmi helyzetébe; a pálya átírása.",
     "SAT: 74,1 s, felső határ 74,7 s", "lezárt"),
    ("E-02", "R-09", "FAT", "A MES a nyomatékadatot hibás értékkel tárolta.", "termékhiba",
     "Az I-07 ICD pontosítása (mértékegység, tizedesjegyek), a fogadó oldal átalakítása; a T6 teszt megismétlése.",
     "FAT ismétlés: 10/10 egyezés", "lezárt"),
    ("E-03", "R-03", "SAT", "A nyomatékmérő kalibrálási bizonyítványa a teszt napján lejárt.", "mérőeszköz",
     "Kalibrált mérőeszköz beszerzése, a mérés megismétlése; a termék nem érintett.",
     "SAT ismétlés: minden kötés tűrésen belül", "lezárt"),
]

MERESEK = [73.8, 74.0, 74.5]


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Követelmény-verifikációs mátrix – sablon", [
        "■ Mire való? A verifikáció tervezése és követése: minden kötelező követelményhez sikerkritérium, verifikációs mód, szint, "
        "helyszín (fázis), felelős, eljárás, eredmény és állapot; az eltérések naplója; konfidenciahatár és sikeres futás próba.",
        "■ Mátrix: legfeljebb 40 követelmény. Csak kötelező („kell”) követelményt vegyél fel. A sikerkritériumot a teszt előtt rögzítsd. "
        "Az Ellenőrzés oszlop jelzi a hiányos sorokat és a nem teljesült, de eltérésjelentés nélküli követelményeket.",
        "■ Eltérések: legfeljebb 20 eltérésjelentés. Az Ok oszlopban különítsd el a termékhibát az eljárás, a környezet és a mérőeszköz "
        "hibájától: termékhiba esetén javítás vagy eltérési engedély, egyébként a teszt megismétlése következik.",
        "■ Állapot: a verifikáció összesítése módonként és állapotonként; a verifikáció akkor zárható le, ha minden követelmény teljesült "
        "vagy eltérési engedélyt kapott, és nincs nyitott eltérés.",
        "■ Statisztika: (1) egyoldali konfidenciahatár egy felső vagy alsó korlátos követelményhez a mérési eredményekből "
        "(Student-féle t-eloszlás); (2) a szükséges mintaelemszám becslése; (3) sikeres futás próba: hány hibátlan próba kell "
        "R megbízhatóság C konfidenciaszintű igazolásához.",
        "A kitöltött példa a KoboCella (kézikönyv 23. fejezet).",
        "Források: ISO/IEC/IEEE 15288:2023, 6.4.9.; ECSS-E-ST-10-02C Rev.1 (2018); Engel (2010); Montgomery (2020); "
        "O'Connor és Kleyner: Practical Reliability Engineering (2012); NASA Systems Engineering Handbook (2016), 5.3. szakasz és D függelék; NASA RP-1358 (1994), 6.1. és 6.5. szakasz.",
    ])

    # ---- Mátrix
    ws = wb.create_sheet("Mátrix")
    cimsor(ws, "Követelmény-verifikációs mátrix", "Csak kötelező követelmények; a sikerkritériumot a teszt előtt kell rögzíteni.")
    fej = ["Azonosító", "Forrás (dokumentum, pont)", "Követelmény", "Sikerkritérium", "Verifikációs mód", "Szint",
           "Helyszín, fázis", "Átvételkor is?", "Végrehajtó", "Eljárás", "Eredmény (dokumentum)", "Állapot",
           "Eltérésjelentés", "Ellenőrzés"]

    def ell(r):
        return (f'=IF(A{r}="","",IF(OR(C{r}="",D{r}="",E{r}="",I{r}=""),"hiányos sor",'
                f'IF(AND(L{r}="nem teljesült",M{r}=""),"eltérésjelentés hiányzik",'
                f'IF(AND(L{r}="eltérési engedély",M{r}=""),"az engedély azonosítója hiányzik",'
                f'IF(AND(L{r}="teljesült",K{r}=""),"az eredmény dokumentuma hiányzik","rendben")))))')

    ut = tablazat(ws, 4, fej, [9, 13, 38, 40, 14, 11, 13, 9, 15, 9, 20, 13, 11, 22],
                  [list(m) for m in MATRIX], bemeneti_oszlopok=tuple(range(1, 14)), kepletek={14: ell},
                  uressor=NR - len(MATRIX))
    legordulo(ws, f"E5:E{ut}", MODOK)
    legordulo(ws, f"F5:F{ut}", ["komponens", "alrendszer", "rendszer"])
    legordulo(ws, f"H5:H{ut}", ["igen", "nem"])
    legordulo(ws, f"L5:L{ut}", ALLAPOTOK)
    piros = PatternFill("solid", fgColor="F6D5D5")
    zold = PatternFill("solid", fgColor="DDEFE4")
    ws.conditional_formatting.add(f"N5:N{ut}", FormulaRule(formula=['AND(N5<>"",N5<>"rendben")'], fill=piros))
    ws.conditional_formatting.add(f"L5:L{ut}", FormulaRule(formula=['OR(L5="teljesült",L5="eltérési engedély")'], fill=zold))
    ws.conditional_formatting.add(f"L5:L{ut}", FormulaRule(formula=['L5="nem teljesült"'], fill=piros))
    megjegyzes(ws["D4"], "Mi számít teljesülésnek? Mintaelemszám, körülmények, döntési szabály. A teszt előtt kell rögzíteni.")
    megjegyzes(ws["H4"], "Igen: a követelményt minden legyártott példány átvételi tesztjén is ellenőrizni kell.")
    ws.freeze_panes = "B5"
    M_UT = ut

    # ---- Eltérések
    ws = wb.create_sheet("Eltérések")
    cimsor(ws, "Eltérésnapló", "Eltérés esetén a verifikációt le kell állítani, és el kell dönteni, hogy a termék vagy az eljárás hibás.")
    fej = ["Azonosító", "Követelmény", "Fázis", "Az eltérés leírása", "Ok", "Intézkedés", "Ismételt verifikáció eredménye", "Állapot"]
    ut = tablazat(ws, 4, fej, [10, 11, 10, 36, 14, 46, 30, 10], [list(e) for e in ELTERESEK],
                  bemeneti_oszlopok=tuple(range(1, 9)), uressor=NE - len(ELTERESEK))
    legordulo(ws, f"E5:E{ut}", ["termékhiba", "eljárás", "környezet", "mérőeszköz", "végrehajtás"])
    legordulo(ws, f"H5:H{ut}", ["nyitott", "lezárt"])
    ws.conditional_formatting.add(f"H5:H{ut}", FormulaRule(formula=['H5="nyitott"'], fill=piros))
    ws.freeze_panes = "B5"
    E_UT = ut

    # ---- Állapot
    ws = wb.create_sheet("Állapot")
    cimsor(ws, "A verifikáció állapota", "Lezárható, ha minden követelmény teljesült vagy eltérési engedélyt kapott, és nincs nyitott eltérés.")
    ws.column_dimensions["A"].width = 26
    for k in range(2, 9):
        ws.column_dimensions[get_column_letter(k)].width = 13
    fejlec(ws, 4, ["Verifikációs mód"] + ALLAPOTOK + ["Összesen"])
    M = "'Mátrix'!"
    for i, mod in enumerate(MODOK):
        r = 5 + i
        szoveg(ws.cell(row=r, column=1), mod)
        for j, al in enumerate(ALLAPOTOK):
            keplet(ws.cell(row=r, column=2 + j),
                   f'=COUNTIFS({M}$E$5:$E${M_UT},$A{r},{M}$L$5:$L${M_UT},{get_column_letter(2 + j)}$4)', "0")
        keplet(ws.cell(row=r, column=7), f"=SUM(B{r}:F{r})", "0", felkov=True)
    ro = 5 + len(MODOK)
    szoveg(ws.cell(row=ro, column=1), "Összesen", felkov=True)
    for k in range(2, 8):
        cl = get_column_letter(k)
        keplet(ws.cell(row=ro, column=k), f"=SUM({cl}5:{cl}{ro - 1})", "0", felkov=True)

    m0 = ro + 2
    fejlec(ws, m0, ["Mutató", "Érték"])
    mutatok = [
        ("Követelmények száma", f"=COUNTA({M}A5:A{M_UT})", "0"),
        ("Állapot nélküli követelmények", f"=B{m0 + 1}-G{ro}", "0"),
        ("Lezárt (teljesült vagy eltérési engedély)", f"=D{ro}+F{ro}", "0"),
        ("Lezárt arány", f'=IF(B{m0 + 1}=0,"",B{m0 + 3}/B{m0 + 1})', "0%"),
        ("Hiányos vagy hibás sor", f'=COUNTIF({M}N5:N{M_UT},"<>rendben")-COUNTBLANK({M}N5:N{M_UT})', "0"),
        ("Nyitott eltérésjelentés", f"=COUNTIF('Eltérések'!H5:H{E_UT},\"nyitott\")", "0"),
        ("Termékhibából eredő eltérés", f"=COUNTIF('Eltérések'!E5:E{E_UT},\"termékhiba\")", "0"),
        ("A verifikáció lezárható?", f'=IF(AND(B{m0 + 1}>0,B{m0 + 3}=B{m0 + 1},B{m0 + 6}=0),"igen","nem")', None),
    ]
    for i, (nev, f, fmt) in enumerate(mutatok):
        szoveg(ws.cell(row=m0 + 1 + i, column=1), nev)
        keplet(ws.cell(row=m0 + 1 + i, column=2), f, fmt, felkov=True)
    megjegyzes(ws.cell(row=m0 + 5, column=1), "Az Ellenőrzés oszlopban nem »rendben« jelzésű sorok száma.")

    ch = BarChart()
    ch.type, ch.grouping, ch.overlap = "bar", "stacked", 100
    diagram_kozos(ch, "Követelmények módonként és állapotonként", None, "követelmény", szel=20, mag=9)
    ch.add_data(Reference(ws, min_col=2, max_col=6, min_row=4, max_row=4 + len(MODOK)), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=4 + len(MODOK)))
    ws.add_chart(ch, "I4")

    # ---- Statisztika
    ws = wb.create_sheet("Statisztika")
    cimsor(ws, "Konfidenciahatár, mintaelemszám, sikeres futás próba", "A KoboCella R-01 és R-03 követelményével kitöltve.")
    ws.column_dimensions["A"].width = 46
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 4
    ws.column_dimensions["D"].width = 14
    szoveg(ws["A4"], "1. Konfidenciahatár", felkov=True)
    bemenetek = [("A követelmény típusa", "felső korlát", None), ("Határérték (U vagy L)", 75, "0.00"),
                 ("Konfidenciaszint (1 − α)", 0.95, "0%")]
    for i, (n, v, f) in enumerate(bemenetek):
        szoveg(ws.cell(row=5 + i, column=1), n)
        bemenet(ws.cell(row=5 + i, column=2), v, f)
    legordulo(ws, "B5", ["felső korlát", "alsó korlát"])
    fejlec(ws, 4, ["Mérési eredmények"], oszlop=4)
    for i in range(NM):
        bemenet(ws.cell(row=5 + i, column=4), MERESEK[i] if i < len(MERESEK) else None, "0.00")
    D = f"D5:D{4 + NM}"
    szamitas = [
        ("Mérések száma (n)", f"=COUNT({D})", "0"),
        ("Átlag", f'=IF(B8=0,"",AVERAGE({D}))', "0.000"),
        ("Szórás (s)", f'=IF(B8<2,"",STDEV({D}))', "0.000"),
        ("t-kvantilis (egyoldali)", f'=IF(B8<2,"",TINV(2*(1-B7),B8-1))', "0.000"),
        ("Konfidenciahatár", f'=IF(B8<2,"",IF(B5="felső korlát",B9+B11*B10/SQRT(B8),B9-B11*B10/SQRT(B8)))', "0.000"),
        ("Döntés", f'=IF(B8<2,"legalább 2 mérés kell",IF(B5="felső korlát",IF(B12<=B6,"teljesül","nem igazolt"),'
                   f'IF(B12>=B6,"teljesül","nem igazolt")))', None),
    ]
    for i, (n, f, fmt) in enumerate(szamitas):
        szoveg(ws.cell(row=8 + i, column=1), n)
        keplet(ws.cell(row=8 + i, column=2), f, fmt, felkov=(i == len(szamitas) - 1))
    megjegyzes(ws["A8"], "A méréseknek függetleneknek kell lenniük. Egymást követő ciklusok helyett például műszakátlagokat használj.")

    szoveg(ws["A16"], "2. A szükséges mintaelemszám (közelítés)", felkov=True)
    bem2 = [("Várható átlag", 74.1, "0.00"), ("Feltételezett szórás", 0.36, "0.000"),
            ("Másodfajú hiba kockázata (β)", 0.10, "0%")]
    for i, (n, v, f) in enumerate(bem2):
        szoveg(ws.cell(row=17 + i, column=1), n)
        bemenet(ws.cell(row=17 + i, column=2), v, f)
    szoveg(ws["A20"], "Szükséges n (normális közelítés)")
    keplet(ws["B20"], '=IF(B17=B6,"",ROUNDUP(((NORMSINV(B7)+NORMSINV(1-B19))*B18/ABS(B6-B17))^2,0))', "0", felkov=True)
    megjegyzes(ws["A20"], "n ≈ ((z₁₋α + z₁₋β)·σ / |határ − várható átlag|)². Kis mintánál a t-eloszlás miatt több mérés kell; "
                          "a pontos értéket (nem centrális t-eloszlással) a notebook számolja.")

    szoveg(ws["A23"], "3. Sikeres futás próba", felkov=True)
    bem3 = [("Igazolandó megbízhatóság (R)", 0.999, "0.0000"), ("Konfidenciaszint (C)", 0.90, "0%"),
            ("Elvégzett hibátlan próbák száma", 8096, "0")]
    for i, (n, v, f) in enumerate(bem3):
        szoveg(ws.cell(row=24 + i, column=1), n)
        bemenet(ws.cell(row=24 + i, column=2), v, f)
    szoveg(ws["A27"], "Szükséges hibátlan próbák száma")
    keplet(ws["B27"], '=IF(OR(B24<=0,B24>=1,B25<=0,B25>=1),"",ROUNDUP(LN(1-B25)/LN(B24),0))', "0", felkov=True)
    szoveg(ws["A28"], "Az elvégzett próbákkal igazolt megbízhatóság")
    keplet(ws["B28"], '=IF(B26<1,"",(1-B25)^(1/B26))', "0.00000", felkov=True)
    szoveg(ws["A29"], "Döntés")
    keplet(ws["B29"], '=IF(B26="","",IF(B26>=B27,"teljesül","kevés próba"))', None, felkov=True)
    megjegyzes(ws["A27"], "n ≥ ln(1 − C) / ln R, ha minden próba sikeres és a próbák függetlenek. Hibás próba esetén a notebook "
                          "binomiális számítását használd.")
    return mentes(wb, "rvm_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
