"""Technikai felülvizsgálat: terv, feltételek, észrevételek (eszközlap: Technikai felülvizsgálat lebonyolítása)."""
import datetime as dt

from openpyxl.formatting.rule import FormulaRule

from _kozos import *  # noqa: F401,F403

D = dt.date
NF, NE = 15, 60
PIROS, ZOLD = PatternFill("solid", fgColor="F6D5D5"), PatternFill("solid", fgColor="DDEFE4")

BELEPES = [
    ("Rendszerarchitektúra (funkciók, elemek, allokáció)", "teljesül", "architektúra-dokumentum 1.2"),
    ("Allokált követelmények nyomonkövetéssel", "teljesül", "követelménynyilvántartás, RTM"),
    ("Interfészjegyzék", "teljesül", "interfészjegyzék 0.9 (24 interfész)"),
    ("A dokkoló tervezési FMEA-ja", "teljesül", "DFMEA 1.0"),
    ("A kölcsönző alkalmazás első prototípusának használhatósági eredményei", "teljesül", "UX-jelentés (12 résztvevő)"),
    ("Az áthelyezési stratégia szimulációja", "teljesül", "szimulációs jelentés"),
    ("A dokumentumok kiküldése legalább 10 nappal előtte", "teljesül", "kiküldve: 2026. április 6."),
    ("A felülvizsgáló csoport kijelölése, köztük független szakértő", "teljesül", "6 bíráló"),
]
SIKER = [
    ("Az architektúra minden rendszerkövetelményt teljesíthet elfogadható kockázattal", "részben", "2 állomáson a járdaszélesség nem igazolt"),
    ("Az interfészek azonosítottak, a kritikus interfészek követelményei rögzítettek", "teljesül", ""),
    ("Minden követelményhez van verifikációs mód", "teljesül", ""),
    ("A fő kockázatok azonosítottak, kezelési tervvel", "részben", "a téli üzemre nincs forgatókönyv"),
    ("A költség és az ütemezés a terv alapján reális", "teljesül", ""),
]
ESZREVETEL = [
    ("É-01", "architektúra 4.2", "Két állomáson (Vár tér, Piac utca) nem igazolt, hogy a dokkoló mellett megmarad a kerekesszékhez szükséges járdaszélesség.", "súlyos", "akadálymentességi képviselő", "Helyszíni felmérés, szükség esetén a dokkolók áthelyezése.", "rendszermérnök", D(2026, 5, 15), "nyitott"),
    ("É-02", "ConOps 3", "A működési koncepcióban nincs forgatókönyv a téli üzemre (hó, jég, alacsony hőmérséklet).", "súlyos", "független rendszermérnök", "Téli forgatókönyv, a dokkoló és a zár hőmérsékleti követelményeinek felülvizsgálata.", "rendszermérnök", D(2026, 5, 31), "nyitott"),
    ("É-03", "interfészjegyzék", "A fizetési szolgáltató interfészének ICD-je még tervezet.", "közepes", "üzemeltető", "Az ICD véglegesítése a szolgáltatóval.", "informatika", D(2026, 5, 20), "folyamatban"),
    ("É-04", "DFMEA F7", "A zár vandalizmus elleni védelmének észlelési pontszáma nem indokolt.", "közepes", "üzemeltető", "Az észlelési mód leírása, szükség esetén teszt.", "szervizmérnök", D(2026, 4, 30), "lezárt"),
    ("É-05", "szimuláció", "A szimuláció nem vizsgálta a rendezvények miatti csúcsterhelést.", "közepes", "önkormányzat", "Két rendezvényes forgatókönyv futtatása.", "rendszermérnök", D(2026, 5, 10), "folyamatban"),
    ("É-06", "UX-jelentés", "A gyengénlátó felhasználók számára a térkép szabad helyeinek jelölése nem megfelelő.", "közepes", "akadálymentességi képviselő", "Szöveges kiírás a térkép mellett (a 2. prototípusban).", "UX-csapat", D(2026, 4, 30), "lezárt"),
    ("É-07", "architektúra 5.1", "Az akkumulátor-cserélési folyamat nincs leírva.", "közepes", "üzemeltető", "A csere folyamatának BPMN-modellje.", "üzemeltetési vezető", D(2026, 5, 15), "folyamatban"),
    ("É-08", "követelmények", "A rendelkezésre állási követelmény mérési módja nem egyértelmű.", "közepes", "független rendszermérnök", "A mérési mód pontosítása (MOP-definíció).", "rendszermérnök", D(2026, 4, 25), "lezárt"),
    ("É-09", "költségterv", "A tartalék nem fedezi az árfolyamkockázatot.", "közepes", "önkormányzat", "Kockázati tartalék emelése vagy árfolyamfedezet.", "projektvezető", D(2026, 4, 30), "lezárt"),
    ("É-10", "interfészjegyzék", "Az I-12 és az I-14 interfész felelőse nincs megadva.", "közepes", "független rendszermérnök", "Felelősök kijelölése.", "rendszermérnök", D(2026, 4, 20), "lezárt"),
    ("É-11", "architektúra 3.3", "Ábra számozási hiba.", "kisebb", "üzemeltető", "Javítás.", "rendszermérnök", D(2026, 4, 20), "lezárt"),
    ("É-12", "követelmények R-21", "Kétértelmű kifejezés („gyorsan”).", "kisebb", "független rendszermérnök", "Átfogalmazás mérhető értékkel.", "rendszermérnök", D(2026, 4, 20), "lezárt"),
    ("É-13", "ConOps 2.4", "A diszpécser szerepe nem egységesen szerepel.", "kisebb", "üzemeltető", "Egységes szerepnév.", "rendszermérnök", D(2026, 4, 20), "lezárt"),
    ("É-14", "DFMEA", "Hiányzik a módosítás dátuma.", "kisebb", "független rendszermérnök", "Javítás.", "szervizmérnök", D(2026, 4, 20), "lezárt"),
    ("É-15", "UX-jelentés", "A résztvevők toborzásának módja nincs leírva.", "kisebb", "akadálymentességi képviselő", "Kiegészítés.", "UX-csapat", D(2026, 4, 25), "lezárt"),
    ("É-16", "szimuláció", "A modell paramétereinek forrása nem hivatkozott.", "kisebb", "független rendszermérnök", "Hivatkozások pótlása.", "rendszermérnök", D(2026, 4, 25), "lezárt"),
    ("É-17", "költségterv", "Az üzemeltetési költség éves bontása hiányzik.", "kisebb", "önkormányzat", "Éves bontás.", "projektvezető", D(2026, 4, 30), "lezárt"),
    ("É-18", "interfészjegyzék", "Elírás az I-03 leírásában.", "kisebb", "üzemeltető", "Javítás.", "rendszermérnök", D(2026, 4, 20), "lezárt"),
    ("É-19", "architektúra 6", "A rövidítésjegyzék hiányos.", "kisebb", "önkormányzat", "Kiegészítés.", "rendszermérnök", D(2026, 4, 20), "lezárt"),
    ("É-20", "ConOps", "Javaslat: turistáknak szóló többnyelvű tájékoztató tábla az állomásokon.", "javaslat", "önkormányzat", "A követelményjelöltek közé felvéve.", "rendszermérnök", None, "lezárt"),
    ("É-21", "UX-jelentés", "Javaslat: hangos útmutató a dokkolón.", "javaslat", "akadálymentességi képviselő", "A követelményjelöltek közé felvéve.", "UX-csapat", None, "lezárt"),
    ("É-22", "szimuláció", "Javaslat: időjárás-előrejelzés bevonása az áthelyezés-tervezésbe.", "javaslat", "független rendszermérnök", "Későbbi bővítésként rögzítve.", "rendszermérnök", None, "lezárt"),
    ("É-23", "költségterv", "Javaslat: szponzorációs lehetőség a dokkolókon.", "javaslat", "önkormányzat", "Elutasítva: a városkép-védelmi szabályokkal ütközik.", "projektvezető", None, "elutasítva"),
]
SULY = ["súlyos", "közepes", "kisebb", "javaslat"]
ALL = ["nyitott", "folyamatban", "lezárt", "elutasítva"]


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Technikai felülvizsgálat – sablon", [
        "■ Mire való? Egy technikai felülvizsgálat (például követelmény-, előzetes vagy részletes tervfelülvizsgálat) előkészítése, "
        "lebonyolítása és lezárása: belépési és sikerességi feltételek, a bírálók észrevételei, az intézkedések követése és az eredmény.",
        "■ Terv: a felülvizsgálat adatai, a belépési feltételek (mi kell ahhoz, hogy a felülvizsgálat megtartható legyen) és a sikerességi "
        "feltételek (mit kell igazolni). Állapot: teljesül / részben / nem teljesül.",
        "■ Észrevételek: legfeljebb 60 észrevétel, súlyossággal (súlyos, közepes, kisebb, javaslat), válasszal, felelőssel, határidővel és állapottal.",
        "■ Összesítés: az észrevételek súlyosság és állapot szerint, a lejárt határidők, és a felülvizsgálat javasolt eredménye "
        "(sikeres / feltételesen sikeres / nem sikeres). Az eredményről a felülvizsgáló csoport dönt; a sablon csak a szabályt alkalmazza.",
        "A kitöltött példa a VárosiBringa előzetes tervfelülvizsgálata (kézikönyv 26. fejezet).",
        "Források: IEEE 15288.2-2014; IEEE 1028-2008; Fagan (1976); NASA Systems Engineering Handbook (2016), 6.7. szakasz és N függelék.",
    ])

    # ---- Terv
    wt = wb.create_sheet("Terv")
    cimsor(wt, "A felülvizsgálat terve")
    wt.column_dimensions["A"].width = 60
    wt.column_dimensions["B"].width = 16
    wt.column_dimensions["C"].width = 40
    adatok = [("Felülvizsgálat", "VárosiBringa előzetes tervfelülvizsgálat (PDR)"), ("Időpont", D(2026, 4, 16)),
              ("Értékelés dátuma (a határidők figyeléséhez)", D(2026, 5, 18)),
              ("Bírálók", "önkormányzat, üzemeltető, akadálymentességi képviselő, független rendszermérnök, ügyfélszolgálat, pénzügy")]
    for i, (k, v) in enumerate(adatok):
        szoveg(wt.cell(row=3 + i, column=1), k, felkov=True)
        bemenet(wt.cell(row=3 + i, column=2), v, "yyyy.mm.dd" if isinstance(v, D) else None)
        wt.merge_cells(start_row=3 + i, start_column=2, end_row=3 + i, end_column=3)
    b0 = 9
    ut_b = tablazat(wt, b0, ["Belépési feltétel", "Állapot", "Bizonyíték"], [60, 16, 40], [list(x) for x in BELEPES],
                    bemeneti_oszlopok=(1, 2, 3), uressor=NF - len(BELEPES))
    s0 = ut_b + 2
    ut_s = tablazat(wt, s0, ["Sikerességi feltétel", "Állapot", "Megjegyzés"], [60, 16, 40], [list(x) for x in SIKER],
                    bemeneti_oszlopok=(1, 2, 3), uressor=NF - len(SIKER))
    for rng in (f"B{b0 + 1}:B{ut_b}", f"B{s0 + 1}:B{ut_s}"):
        legordulo(wt, rng, ["teljesül", "részben", "nem teljesül"])
        a = rng.split(":")[0]
        wt.conditional_formatting.add(rng, FormulaRule(formula=[f'{a}="teljesül"'], fill=ZOLD))
        wt.conditional_formatting.add(rng, FormulaRule(formula=[f'OR({a}="részben",{a}="nem teljesül")'], fill=PIROS))
    TB = (b0 + 1, ut_b)
    TS = (s0 + 1, ut_s)

    # ---- Észrevételek
    we = wb.create_sheet("Észrevételek")
    cimsor(we, "Észrevételek", "Minden észrevételhez válasz, felelős és határidő tartozik; a lezárást a bíráló is elfogadja.")
    fej = ["Az.", "Dokumentum, hely", "Észrevétel", "Súlyosság", "Bíráló", "Válasz, intézkedés", "Felelős", "Határidő", "Állapot", "Lejárt?"]
    ut = tablazat(we, 4, fej, [7, 18, 52, 11, 22, 44, 18, 12, 12, 9], [list(x) for x in ESZREVETEL],
                  bemeneti_oszlopok=tuple(range(1, 10)),
                  kepletek={10: lambda r: f"=IF(OR(A{r}=\"\",H{r}=\"\",I{r}=\"lezárt\",I{r}=\"elutasítva\"),\"\",IF(H{r}<'Terv'!$B$5,\"igen\",\"nem\"))"},
                  uressor=NE - len(ESZREVETEL), formatumok={8: "yyyy.mm.dd"})
    legordulo(we, f"D5:D{ut}", SULY)
    legordulo(we, f"I5:I{ut}", ALL)
    we.conditional_formatting.add(f"D5:D{ut}", FormulaRule(formula=['D5="súlyos"'], fill=PIROS))
    we.conditional_formatting.add(f"J5:J{ut}", FormulaRule(formula=['J5="igen"'], fill=PIROS))
    we.freeze_panes = "C5"
    E_UT = ut

    # ---- Összesítés
    wo = wb.create_sheet("Összesítés")
    cimsor(wo, "Összesítés", "A javasolt eredmény szabálya: sikeres, ha minden sikerességi feltétel teljesül és nincs nyitott súlyos észrevétel; "
                             "feltételesen sikeres, ha a nyitott súlyos észrevételekhez felelős és határidő tartozik; egyébként nem sikeres.")
    wo.column_dimensions["A"].width = 46
    fejlec(wo, 4, ["Súlyosság"] + ALL + ["Összesen"], [46, 11, 12, 11, 12, 11])
    S, A_, = f"'Észrevételek'!$D$5:$D${E_UT}", f"'Észrevételek'!$I$5:$I${E_UT}"
    for i, s in enumerate(SULY):
        r = 5 + i
        szoveg(wo.cell(row=r, column=1), s)
        for j, a in enumerate(ALL):
            keplet(wo.cell(row=r, column=2 + j), f'=COUNTIFS({S},$A{r},{A_},"{a}")', "0")
        keplet(wo.cell(row=r, column=6), f"=SUM(B{r}:E{r})", "0", True)
    rt = 5 + len(SULY)
    szoveg(wo.cell(row=rt, column=1), "Összesen", felkov=True)
    for k in range(2, 7):
        cl = get_column_letter(k)
        keplet(wo.cell(row=rt, column=k), f"=SUM({cl}5:{cl}{rt - 1})", "0", True)
    m0 = rt + 2
    T = "'Terv'!"
    nyitott_sulyos = f'COUNTIFS({S},"súlyos",{A_},"nyitott")+COUNTIFS({S},"súlyos",{A_},"folyamatban")'
    terv_nelkul = (f"SUMPRODUCT(({S}=\"súlyos\")*(({A_}=\"nyitott\")+({A_}=\"folyamatban\"))*"
                   f"((LEN('Észrevételek'!$G$5:$G${E_UT})=0)+(LEN('Észrevételek'!$H$5:$H${E_UT})=0)>0))")
    mut = [
        ("Belépési feltételek: nem teljesül vagy részben", f'=COUNTIF({T}B{TB[0]}:B{TB[1]},"részben")+COUNTIF({T}B{TB[0]}:B{TB[1]},"nem teljesül")', "0"),
        ("A felülvizsgálat megtartható?", f'=IF(B{m0 + 1}=0,"igen","nem: előbb a belépési feltételeket kell teljesíteni")', None),
        ("Sikerességi feltételek: nem teljesül vagy részben", f'=COUNTIF({T}B{TS[0]}:B{TS[1]},"részben")+COUNTIF({T}B{TS[0]}:B{TS[1]},"nem teljesül")', "0"),
        ("Nyitott súlyos észrevételek", f"={nyitott_sulyos}", "0"),
        ("Nyitott súlyos észrevétel felelős vagy határidő nélkül", f"={terv_nelkul}", "0"),
        ("Lejárt határidejű nyitott észrevételek", f"=COUNTIF('Észrevételek'!J5:J{E_UT},\"igen\")", "0"),
        ("Javasolt eredmény (a felülvizsgáló csoport dönt)",
         f'=IF(B{m0 + 2}<>"igen","nem tartható meg",IF(AND(B{m0 + 3}=0,B{m0 + 4}=0),"sikeres",'
         f'IF(B{m0 + 5}=0,"feltételesen sikeres: a nyitott tételeket a következő felülvizsgálat előtt le kell zárni","nem sikeres")))', None),
    ]
    for i, (n, f, fm) in enumerate(mut):
        szoveg(wo.cell(row=m0 + 1 + i, column=1), n)
        keplet(wo.cell(row=m0 + 1 + i, column=2), f, fm, i in (1, 6))
        if i in (1, 6):
            wo.merge_cells(start_row=m0 + 1 + i, start_column=2, end_row=m0 + 1 + i, end_column=6)
    ch = BarChart()
    ch.type, ch.grouping, ch.overlap = "bar", "stacked", 100
    diagram_kozos(ch, "Észrevételek súlyosság és állapot szerint", None, "darab", 18, 8)
    ch.add_data(Reference(wo, min_col=2, max_col=5, min_row=4, max_row=4 + len(SULY)), titles_from_data=True)
    ch.set_categories(Reference(wo, min_col=1, min_row=5, max_row=4 + len(SULY)))
    wo.add_chart(ch, "H4")
    return mentes(wb, "felulvizsgalat_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
