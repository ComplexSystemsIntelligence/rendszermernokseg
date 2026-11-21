"""PDCA-, 8D- és DMAIC-munkalapok (eszközlap: PDCA, 8D és DMAIC)."""
import datetime as dt

from openpyxl.formatting.rule import FormulaRule

from _kozos import *  # noqa: F401,F403

D = dt.date
ALLAPOT = ["nem kezdődött el", "folyamatban", "kész"]

D8 = [
    ("D1", "A csapat összeállítása", "Rendszermérnök (vezető), üzemeltetési vezető, a dokkoló beszállítójának szervizmérnöke, diszpécser, ügyfélszolgálati munkatárs.", "rendszermérnök", D(2027, 1, 12), D(2027, 1, 12)),
    ("D2", "A probléma leírása", "Három hét alatt 12 bejelentés: a dokkoló a kerékpár visszahelyezése után nem zárt. Érintett: 4 állomás, mind árnyékos helyen; az esetek reggel 6 és 9 óra között, −3 °C alatti hőmérsékletnél történtek. Nem érintett: a napos állomások, a nappali órák.", "rendszermérnök", D(2027, 1, 13), D(2027, 1, 13)),
    ("D3", "Azonnali (elszigetelő) intézkedés", "Az alkalmazás a visszaadás után a zár állapotát is ellenőrzi, sikertelen zárásnál a szomszédos dokkolóhoz irányít; a diszpécser reggelente ellenőrzi a négy állomást. Hatékonyság: az ügyfelet érintő díjvita megszűnt.", "üzemeltetési vezető", D(2027, 1, 14), D(2027, 1, 14)),
    ("D4", "A gyökérok feltárása és igazolása", "Ok-okozati diagram; hűtőkamrás teszt: −5 °C alatt a zárnyelv kenőanyaga besűrűsödik, a reteszcsap nem ugrik be teljesen. Az ok a hibát ki- és bekapcsolja (−5 °C alatt 10/10 hiba, +5 °C-on 0/10).", "szervizmérnök", D(2027, 1, 21), D(2027, 1, 20)),
    ("D5", "A javító intézkedések kiválasztása", "Alacsony hőmérsékleten is működő kenőanyag és erősebb zárnyelvrugó; elvetve: fűtött zár (energiaigény, költség).", "rendszermérnök", D(2027, 1, 25), D(2027, 1, 25)),
    ("D6", "Bevezetés és a hatékonyság igazolása", "Hűtőkamra: −15 °C-ig 20/20 sikeres zárás; két állomáson két hét terepi próba hiba nélkül; ezután mind a 300 dokkoló átalakítása.", "szervizmérnök", D(2027, 2, 15), D(2027, 2, 19)),
    ("D7", "A megismétlődés megelőzése", "A dokkoló tervezési FMEA-jának frissítése (alacsony hőmérséklet mint hibaok), a kenőanyag-specifikáció módosítása, téli ellenőrzőlista; tanulság a következő beszerzés követelményeihez.", "rendszermérnök", D(2027, 2, 26), D(2027, 2, 26)),
    ("D8", "A csapat elismerése, lezárás", "Lezáró megbeszélés, a 8D-jelentés archiválása, a csapat munkájának elismerése.", "üzemeltetési vezető", D(2027, 3, 1), D(2027, 3, 1)),
]

DMAIC = [
    ("Meghatározás", "Mi a probléma, mekkora, kit érint, mi a cél?", "projektlap, SIPOC, Pareto-diagram", "jóváhagyott projektlap", "A cél mérhető és határidős? A hatókör rögzített?", D(2026, 3, 31), "kész"),
    ("Mérés", "Mekkora a jelenlegi teljesítmény, megbízhatóak-e az adatok?", "MES-napló, adatminőség-ellenőrzés, folyamatábra", "kiinduló érték, mérési terv", "A mérőszám definíciója egyértelmű? Az adatok teljesek?", D(2026, 4, 10), "kész"),
    ("Elemzés", "Mi a gyökérok, és mi bizonyítja?", "ok-okozati diagram, rétegzés, 5 miért", "igazolt gyökérokok", "A gyökérokot adatok igazolják?", D(2026, 4, 24), "kész"),
    ("Fejlesztés", "Milyen megoldás szünteti meg a gyökérokot, és működik-e?", "megoldások összevetése, kísérleti bevezetés két gépen", "kipróbált megoldás, bevezetési terv", "A kísérleti eredmény eléri a célt? A kockázatok kezeltek?", D(2026, 5, 29), "kész"),
    ("Szabályozás", "Hogyan marad fenn a javulás?", "egyedi értékes kontrollkártya, eljárásleírás, képzés", "szabályozási terv, átadás a folyamatgazdának", "A folyamatgazda átvette? A mérőszám stabil?", D(2026, 6, 30), "kész"),
]

MEROSZAM = [("2026-02", 1150), ("2026-03", 1120), ("2026-04", 1080), ("2026-05", 640), ("2026-06", 410), ("2026-07", 385), ("2026-08", 380)]


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "PDCA, 8D és DMAIC – munkalapok", [
        "■ Mire való? A folyamatos fejlesztés három szervezett ciklusának dokumentálása: PDCA (kisebb fejlesztések), 8D (reklamáció, súlyos hiba), "
        "DMAIC (krónikus, mérhető teljesítményhiány). Mindhárom ugyanarra a logikára épül: a probléma pontos leírása, a gyökérok igazolása, "
        "a megoldás kipróbálása, a hatás mérése és a változás rögzítése.",
        "■ PDCA-lap: egyetlen lapon (A3-szemlélet) a háttér, a jelenlegi állapot, a cél, az elemzés, a terv, a végrehajtás, az ellenőrzés és a beavatkozás.",
        "■ 8D-jelentés: a D1–D8 lépések tartalommal, felelőssel, határidővel és állapottal; az azonnali (D3) és a tartós (D5–D6) intézkedés "
        "elválasztásával. A lap jelzi a késésben lévő lépéseket a megadott értékelési dátumhoz képest.",
        "■ DMAIC-projektlap: a probléma, a cél, a hatókör és a csapat; a fázisok fő kérdéseivel, eszközeivel, kimeneteivel és fázislezáró "
        "ellenőrző kérdéseivel; a mérőszám alakulása diagrammal.",
        "■ Intézkedések: a ciklusokból adódó intézkedések közös nyilvántartása (felelős, határidő, állapot, a hatékonyság ellenőrzése).",
        "A kitöltött példák: PDCA – a KoboCella nyugtázó gombjának áthelyezése (kézikönyv 24. fejezet); 8D – a VárosiBringa téli zárhibái; "
        "DMAIC – a ForgácsTech anyagra várása (kézikönyv 25. fejezet).",
        "Források: Deming: Out of the Crisis (1986); VDA QMC: 8D – Problem Solving in 8 Disciplines (2018); Schroeder és mtsai (2008); "
        "Montgomery: Introduction to Statistical Quality Control (2020).",
    ])

    # ---- PDCA
    wp = wb.create_sheet("PDCA-lap")
    cimsor(wp, "PDCA-lap", "KoboCella: a hibanyugtázás áthelyezése a kezelői oldalra.")
    wp.column_dimensions["A"].width = 26
    wp.column_dimensions["B"].width = 90
    mezok = [
        ("Téma", "A hibanyugtázás helye a KoboCellánál"),
        ("Felelős, dátum", "rendszermérnök, ergonómus; 2026. szeptember"),
        ("P – háttér", "A validáció első hetében a kezelők a hibaelhárítási forgatókönyvekben (elakadt csavar, hiányzó fedél) gyakran a cella mögé mentek nyugtázni."),
        ("P – jelenlegi állapot", "Műszakonként átlagosan 14 alkalommal ment a kezelő a cella mögé; alkalmanként kb. 40 s; a nyugtázó gomb a hibaüzenet kijelzőjétől 2,5 m-re, a cella hátoldalán volt."),
        ("P – cél", "A kezelő minden hibát a kezelői oldalról nyugtázzon; a hibaelhárítás ideje csökkenjen; a biztonsági funkciók ne változzanak."),
        ("P – elemzés", "A gomb helyét a villamos tervben a vezérlőszekrény közelsége határozta meg; a kezelői feladatelemzés (HTA) a nyugtázást nem tartalmazta."),
        ("P – terv", "Második nyugtázó gomb a kezelői oldalon, a kijelző mellett; a biztonsági mérnök jóváhagyásával (a biztonsági funkció nem érintett); próba egy műszakban egy hétig."),
        ("D – végrehajtás", "A gombot a karbantartás beépítette; az I-06 interfész ICD-je és a kezelési útmutató ideiglenes kiegészítése elkészült."),
        ("C – ellenőrzés", "A próbahéten a cella mögé menetelek száma 0; a hibaelhárítás átlagos ideje 95 s-ról 52 s-ra csökkent; a kezelők egyöntetűen jobbnak ítélték."),
        ("A – beavatkozás", "A megoldás szabványosítása mindkét műszakra; az ICD, a kezelési útmutató és a HTA frissítése; tanulság a következő cellák terveihez: a nyugtázás a kezelői feladat része."),
    ]
    for i, (k, v) in enumerate(mezok):
        szoveg(wp.cell(row=3 + i, column=1), k, felkov=True)
        bemenet(wp.cell(row=3 + i, column=2), v)
        wp.row_dimensions[3 + i].height = 32

    # ---- 8D
    w8 = wb.create_sheet("8D-jelentés")
    cimsor(w8, "8D-jelentés", "VárosiBringa: a dokkoló téli zárhibái.")
    fejmezok = [("Azonosító", "8D-2027-03"), ("Termék, rendszer", "VárosiBringa dokkoló (zárszerkezet)"), ("Nyitás dátuma", D(2027, 1, 12)),
                ("Értékelés dátuma", D(2027, 2, 20))]
    w8.column_dimensions["A"].width = 10
    w8.column_dimensions["B"].width = 30
    for i, (k, v) in enumerate(fejmezok):
        szoveg(w8.cell(row=3 + i, column=2), k, felkov=True)
        bemenet(w8.cell(row=3 + i, column=3), v, "yyyy.mm.dd" if isinstance(v, D) else None)
    megjegyzes(w8["B6"], "Ehhez a dátumhoz viszonyítva jelzi a lap a késésben lévő lépéseket.")
    fej = ["Lépés", "Megnevezés", "Tartalom", "Felelős", "Határidő", "Kész", "Állapot", "Késés [nap]"]
    sorok = []
    for k, (az, nev, tart, fel, hat, kesz) in enumerate(D8):
        allapot = "kész" if kesz <= D(2027, 2, 20) else "folyamatban"
        sorok.append([az, nev, tart, fel, hat, kesz if allapot == "kész" else None, allapot])
    ut = tablazat(w8, 8, fej, [8, 30, 80, 18, 12, 12, 16, 11], sorok, bemeneti_oszlopok=(3, 4, 5, 6, 7),
                  kepletek={8: lambda r: f'=IF(OR(E{r}="",G{r}="kész"),"",MAX(0,$C$6-E{r}))'},
                  formatumok={5: "yyyy.mm.dd", 6: "yyyy.mm.dd", 8: "0"})
    for r in range(9, ut + 1):
        w8.row_dimensions[r].height = 60
    legordulo(w8, f"G9:G{ut}", ALLAPOT)
    w8.conditional_formatting.add(f"H9:H{ut}", FormulaRule(formula=["AND(ISNUMBER(H9),H9>0)"], fill=PatternFill("solid", fgColor="F6D5D5")))
    w8.conditional_formatting.add(f"G9:G{ut}", FormulaRule(formula=['G9="kész"'], fill=PatternFill("solid", fgColor="DDEFE4")))
    szoveg(w8.cell(row=ut + 2, column=2), "Kész lépések", felkov=True)
    keplet(w8.cell(row=ut + 2, column=3), f'=COUNTIF(G9:G{ut},"kész")&" / 8"')
    szoveg(w8.cell(row=ut + 3, column=2), "Késésben lévő lépések", felkov=True)
    keplet(w8.cell(row=ut + 3, column=3), f'=COUNTIF(H9:H{ut},">0")', "0")
    szoveg(w8.cell(row=ut + 4, column=2), "Átfutás a lezárásig [nap]", felkov=True)
    keplet(w8.cell(row=ut + 4, column=3), f'=IF(COUNTIF(G9:G{ut},"kész")<8,"nincs lezárva",MAX(F9:F{ut})-C5)', "0")

    # ---- DMAIC
    wd = wb.create_sheet("DMAIC-projektlap")
    cimsor(wd, "DMAIC-projektlap", "ForgácsTech: az anyagra várás csökkentése.")
    wd.column_dimensions["A"].width = 24
    for c, w in zip("BCDEFG", [40, 34, 30, 40, 12, 14]):
        wd.column_dimensions[c].width = w
    pl = [("Probléma", "Az anyagra várás havi 1120 perc, a gépek állásidejének 31%-a (MES-napló, 2026. március)."),
          ("Üzleti indoklás", "A határidő-tartás a két legnagyobb vevő keretszerződésének feltétele; az állásidő a szűk keresztmetszetet jelentő megmunkáló központokon a legnagyobb."),
          ("Mérőszám és cél", "Havi anyagra várás a megmunkáló gépeken; kiinduló 1120 perc, cél ≤ 400 perc 2026. június végéig."),
          ("Hatókör", "Benne: anyagkiadás, ütemezés, raktár–csarnok anyagáramlás. Kívül: beszerzés, beszállítói teljesítmény."),
          ("Csapat", "projektvezető: termelésvezető; tagok: logisztikai vezető, raktáros, két műszakvezető, MES-kulcsfelhasználó; támogató: ügyvezető.")]
    for i, (k, v) in enumerate(pl):
        szoveg(wd.cell(row=3 + i, column=1), k, felkov=True)
        bemenet(wd.cell(row=3 + i, column=2), v)
        wd.merge_cells(start_row=3 + i, start_column=2, end_row=3 + i, end_column=5)
        wd.row_dimensions[3 + i].height = 30
    ut = tablazat(wd, 9, ["Fázis", "Fő kérdés", "Eszközök", "Kimenet", "Fázislezáró ellenőrző kérdések", "Határidő", "Állapot"],
                  [24, 40, 34, 30, 40, 12, 14], [list(x) for x in DMAIC], bemeneti_oszlopok=(2, 3, 4, 5, 6, 7),
                  formatumok={6: "yyyy.mm.dd"})
    for r in range(10, ut + 1):
        wd.row_dimensions[r].height = 34
    legordulo(wd, f"G10:G{ut}", ALLAPOT)
    m0 = ut + 3
    szoveg(wd.cell(row=m0 - 1, column=1), "A mérőszám alakulása", felkov=True)
    tablazat(wd, m0, ["Hónap", "Anyagra várás [perc/hó]", "Cél"], [24, 40, 34],
             [[h, v] for h, v in MEROSZAM], bemeneti_oszlopok=(1, 2),
             kepletek={3: lambda r: "=400"}, uressor=5, formatumok={2: "0", 3: "0"})
    ch = LineChart()
    diagram_kozos(ch, "Havi anyagra várás és a cél", "hónap", "perc/hó", 18, 8)
    ch.add_data(Reference(wd, min_col=2, max_col=3, min_row=m0, max_row=m0 + len(MEROSZAM)), titles_from_data=True)
    ch.set_categories(Reference(wd, min_col=1, min_row=m0 + 1, max_row=m0 + len(MEROSZAM)))
    wd.add_chart(ch, f"E{m0}")

    # ---- Intézkedések
    wi = wb.create_sheet("Intézkedések")
    cimsor(wi, "Intézkedési terv", "Minden intézkedéshez felelős, határidő és a hatékonyság ellenőrzése tartozik.")
    szoveg(wi["A3"], "Értékelés dátuma", felkov=True)
    bemenet(wi["B3"], D(2026, 6, 15), "yyyy.mm.dd")
    sorok = [
        ("DMAIC-ForgácsTech", "A MES átsoroláskor ellenőrzi az anyag rendelkezésre állását", "MES-kulcsfelhasználó", D(2026, 5, 15), "kész", "átsorolás utáni várakozás: 26 → 3 eset/hó"),
        ("DMAIC-ForgácsTech", "Anyagkiadás kétóránként az ütemterv alapján", "logisztikai vezető", D(2026, 5, 15), "kész", "a raktári kiadások 92%-a ütemterv szerinti"),
        ("DMAIC-ForgácsTech", "Napi I-MR kártya a műszakvezetői megbeszélésen", "termelésvezető", D(2026, 6, 1), "kész", "a kártya működik; egy jelzés (beszállítói késés)"),
        ("DMAIC-ForgácsTech", "Átmeneti tárolóhely kialakítása a csarnokban", "karbantartás", D(2026, 6, 10), "folyamatban", ""),
        ("8D-VárosiBringa", "Téli ellenőrzőlista bevezetése", "üzemeltetési vezető", D(2027, 2, 26), "nem kezdődött el", ""),
    ]
    ut = tablazat(wi, 5, ["Forrás", "Intézkedés", "Felelős", "Határidő", "Állapot", "A hatékonyság ellenőrzése", "Lejárt?"],
                  [20, 52, 20, 12, 16, 44, 9], [list(x) for x in sorok], bemeneti_oszlopok=(1, 2, 3, 4, 5, 6),
                  kepletek={7: lambda r: f'=IF(OR(B{r}="",E{r}="kész",D{r}=""),"",IF(D{r}<$B$3,"igen","nem"))'},
                  uressor=15, formatumok={4: "yyyy.mm.dd"})
    legordulo(wi, f"E6:E{ut}", ALLAPOT)
    wi.conditional_formatting.add(f"G6:G{ut}", FormulaRule(formula=['G6="igen"'], fill=PatternFill("solid", fgColor="F6D5D5")))
    szoveg(wi.cell(row=ut + 2, column=1), "Nyitott intézkedések", felkov=True)
    keplet(wi.cell(row=ut + 2, column=2), f'=COUNTA(B6:B{ut})-COUNTIF(E6:E{ut},"kész")', "0", True)
    szoveg(wi.cell(row=ut + 3, column=1), "Lejárt határidejű", felkov=True)
    keplet(wi.cell(row=ut + 3, column=2), f'=COUNTIF(G6:G{ut},"igen")', "0", True)
    szoveg(wi.cell(row=ut + 4, column=1), "Kész, de hatékonyság-ellenőrzés nélkül", felkov=True)
    keplet(wi.cell(row=ut + 4, column=2), f'=COUNTIFS(E6:E{ut},"kész",F6:F{ut},"")', "0", True)
    return mentes(wb, "pdca_8d_dmaic_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
