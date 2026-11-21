"""Hat gondolkodó kalap – ülésterv és jegyzet (eszközlap: Hat gondolkodó kalap)."""
from _kozos import *  # noqa: F401,F403

KALAPOK = [("kék", "a cél és a menet rögzítése", "Mi a megbeszélés célja? Milyen sorrendben haladunk?", 5),
           ("fehér", "tények, adatok", "Mit tudunk biztosan? Milyen adat hiányzik, és honnan szerezzük meg?", 10),
           ("zöld", "új lehetőségek", "Milyen más megoldások jöhetnek szóba? Hogyan lehetne a gyenge pontokat kiküszöbölni?", 10),
           ("sárga", "előnyök", "Miért lehetünk bizakodók? Mi az értéke a javaslatnak?", 8),
           ("fekete", "kockázatok, kritika", "Mi mehet félre? Milyen kockázatokra kell figyelnünk?", 10),
           ("piros", "megérzések", "Mi a zsigeri reakciónk? (indoklás nélkül, egy-két szóban)", 4),
           ("kék", "összegzés, következő lépések", "Mire jutottunk? Ki mit tesz, és mikorra?", 8)]
JEGYZET = {
    "fehér": ["a késések 38%-a, átlagosan 4 munkanap", "a beruházási keret 45 MFt", "az M3 első üteme 14 MFt, az M1 42 MFt",
              "nincs adatunk arról, mennyi idő alatt tanulják meg a műszakvezetők az ütemezőt"],
    "zöld": ["az első ütem egy bővíthető platformon induljon", "kísérleti üzem két géppel, egy hónapig",
             "a sürgősségi átsorolás naplózása már az első ütemben"],
    "sárga": ["gyors megtérülés, kis kockázat", "a csapat hamar látja az eredményt", "a tapasztalatok a második ütem követelményeit pontosítják"],
    "fekete": ["két ütem két átállást jelent a műhelynek", "ha a platform mégsem bővíthető, zsákutcába jutunk",
               "az első ütem után elfogyhat a lendület"],
    "piros": ["bizakodó", "óvatos", "kíváncsi"],
}


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Hat gondolkodó kalap – sablon", [
        "■ Mire való? Egy megbeszélésen a gondolkodásmódok időbeli szétválasztása: a csoport egyszerre csak egyféle módon gondolkodik (de Bono).",
        "1. Az „Ülésterv” lapon rögzítsd a megbeszélés témáját, a kalapok sorrendjét és az egyes kalapokra szánt időt. A kék kalapot a moderátor viseli: ő nyit, zár és vált.",
        "2. A megbeszélés alatt a „Jegyzet” lap megfelelő oszlopába kerüljenek a gondolatok. Fekete kalapnál kritikát gyűjtünk, zöldnél tilos kritizálni.",
        "3. Az „Összegzés” lapon rögzítsd a fő megállapításokat, a döntéseket és a következő lépéseket felelőssel és határidővel.",
        "■ Példa: a ForgácsTech fokozatos MES-bevezetésének megvitatása (kézikönyv 10. fejezet).",
    ])
    ws = wb.create_sheet("Ülésterv")
    cimsor(ws, "Ülésterv")
    szoveg(ws["A3"], "Téma:", felkov=True)
    bemenet(ws["B3"], "Fokozatos MES-bevezetés (M3) a ForgácsTech-nél: milyen feltételekkel javasoljuk?")
    ws.merge_cells("B3:E3")
    u = tablazat(ws, 5, ["Sorrend", "Kalap", "Gondolkodásmód", "Vezérkérdések", "Idő [perc]"], [9, 10, 28, 70, 10],
                 [[i + 1, k, g, q, t] for i, (k, g, q, t) in enumerate(KALAPOK)], bemeneti_oszlopok=range(1, 6), uressor=5)
    legordulo(ws, f"B6:B{u}", ["kék", "fehér", "piros", "fekete", "sárga", "zöld"])
    szoveg(ws.cell(row=u + 2, column=4), "Teljes időtartam [perc]", felkov=True)
    keplet(ws.cell(row=u + 2, column=5), f"=SUM(E6:E{u})", felkov=True)
    jg = wb.create_sheet("Jegyzet")
    cimsor(jg, "Jegyzet kalaponként")
    sor = ["fehér", "piros", "fekete", "sárga", "zöld", "kék"]
    fejlec(jg, 4, [f"{k} kalap" for k in sor], [34] * 6)
    for j, k in enumerate(sor):
        for i in range(25):
            lst = JEGYZET.get(k, [])
            bemenet(jg.cell(row=5 + i, column=1 + j), lst[i] if i < len(lst) else None)
    for j in range(6):
        col = get_column_letter(1 + j)
        keplet(jg.cell(row=31, column=1 + j), f'="Bejegyzések: "&COUNTA({col}5:{col}29)')
    os_ = wb.create_sheet("Összegzés")
    cimsor(os_, "Összegzés")
    tablazat(os_, 4, ["Típus", "Tartalom", "Felelős", "Határidő"], [16, 70, 18, 14],
             [["megállapítás", "Az M3 kockázata kicsi, de a bővíthetőség feltétel.", "", ""],
              ["döntés", "Az M3-at javasoljuk, bővíthető platformú beszállítótól.", "projektvezető", ""],
              ["következő lépés", "A beszállítói ajánlatkérésbe a bővíthetőség igazolását kötelező feltételként felvenni.", "beszerzés", ""],
              ["következő lépés", "Kísérleti üzem két gépen, egy hónap.", "termelési vezető", ""]],
             bemeneti_oszlopok=(1, 2, 3, 4), uressor=10)
    legordulo(os_, "A5:A18", ["megállapítás", "döntés", "nyitott kérdés", "következő lépés"])
    return mentes(wb, "hat_kalap_sablon.xlsx")
