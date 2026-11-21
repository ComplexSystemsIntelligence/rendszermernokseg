"""Követelménynyilvántartás automatikus megfogalmazás-ellenőrzéssel (eszközlap: Követelményírás)."""
from _kozos import *  # noqa: F401,F403

TIPUS = ["funkcionális", "teljesítmény", "interfész", "környezeti", "emberi tényezők", "megbízhatóság", "biztonság", "korlát", "egyéb"]
PRIOR = ["kötelező", "fontos", "kívánatos"]
VERIF = ["vizsgálat", "elemzés", "bemutatás", "teszt"]
ALLAPOT = ["javasolt", "jóváhagyott", "alapvonalban", "verifikált", "törölt"]
SZOTAR = ["megfelelő", "megfelelően", "gyors", "gyorsan", "rugalmas", "felhasználóbarát", "könnyen", "könnyű",
          "lehetőleg", "optimális", "maximalizál", "minimalizál", "kellően", "általában", "szükség szerint",
          "stb.", "és/vagy", "többek között", "ésszerű", "hatékony", "megbízható", "biztonságos", "modern", "korszerű"]

PELDA = [
    ("R-01", "A cellának egy motort legfeljebb 75 s alatt kell összeszerelnie.", "teljesítmény", "Ütemidő 88,7 s, OEE 85% → 75 s.", "EF-01, MOE-1", "kötelező", "teszt", "rendszermérnök", "alapvonalban", "igen"),
    ("R-02", "A cella havi rendelkezésre állásának el kell érnie a 95%-ot.", "megbízhatóság", "A 85%-os OEE-hez szükséges.", "MOE-1", "kötelező", "elemzés", "rendszermérnök", "alapvonalban", "igen"),
    ("R-03", "A cellának a nyolc csavart 4,0 ± 0,2 Nm nyomatékkal kell meghúznia.", "teljesítmény", "A vevő műszaki előírása.", "vevői rajz", "kötelező", "teszt", "minőségügy", "alapvonalban", "nem"),
    ("R-05", "A munkaasztalon végzett minden műveletnek legfeljebb 20°-os törzshajlítással elvégezhetőnek kell lennie.", "emberi tényezők", "Az operátorok panaszai; ergonómiai elemzés.", "EF-03", "kötelező", "elemzés", "ergonómus", "jóváhagyott", "nem"),
    ("R-07", "Ha egy csavar nyomatéka a tűrésen kívül esik, akkor a cellának a motort hibásként kell megjelölnie.", "funkcionális", "Selejt nem juthat a vevőhöz.", "R-03", "kötelező", "teszt", "robotintegrátor", "jóváhagyott", "nem"),
    ("R-09", "A cellának minden kész motor nyomatékadatait a motor azonosítójához rendelve kell a MES-nek átadnia.", "interfész", "Nyomonkövethetőség a vevő felé.", "EF-07", "kötelező", "bemutatás", "informatika", "jóváhagyott", "nem"),
    ("R-11", "Amíg személy tartózkodik a védőzónában, a kobot sebességének legfeljebb 250 mm/s-nak kell lennie.", "biztonság", "Kockázatértékelés, TBR: a végleges értéket a biztonsági szakértő adja meg.", "kockázatértékelés", "kötelező", "teszt", "munkavédelem", "javasolt", "igen"),
    ("R-15", "A cellának el kell férnie a jelenlegi 6 × 4 m-es területen.", "korlát", "Csarnokkiosztás.", "üzemigazgató", "kötelező", "vizsgálat", "gyártástechnológia", "alapvonalban", "nem"),
    # szándékosan hibás példák
    ("R-30", "A cellának gyorsnak és felhasználóbarátnak kell lennie.", "egyéb", "", "", "fontos", "", "", "javasolt", "nem"),
    ("R-31", "A cellának meg kell jelenítenie a hibákat és naplóznia kell az eseményeket, stb.", "funkcionális", "Karbantartás kérése.", "EF-05", "fontos", "bemutatás", "robotintegrátor", "javasolt", "nem"),
    ("R-32", "Az operátor ellenőrzi a kész motort.", "egyéb", "", "", "fontos", "", "", "javasolt", "nem"),
    ("R-33", "A csavarozó egység pontossága TBD.", "teljesítmény", "", "R-03", "kötelező", "teszt", "", "javasolt", "nem"),
]

FEJ = ["Azonosító", "Követelmény szövege", "Típus", "Indoklás", "Forrás", "Prioritás", "Verifikációs mód", "Felelős",
       "Állapot", "KDR", "»kell« darab", "Kétértelmű kifejezés", "Van szám?", "Ellenőrzés"]
SZEL = [9, 52, 15, 30, 16, 11, 13, 16, 13, 7, 8, 11, 8, 46]


def kepletek(utolso_szotar):
    szot = f"Szótár!$A$5:$A${utolso_szotar}"
    return {
        11: lambda r: f'=IF(B{r}="","",(LEN(LOWER(B{r}))-LEN(SUBSTITUTE(LOWER(B{r}),"kell","")))/4)',
        12: lambda r: f'=IF(B{r}="","",SUMPRODUCT(({szot}<>"")*ISNUMBER(SEARCH({szot},B{r}))))',
        13: lambda r: (f'=IF(B{r}="","",IF(SUMPRODUCT(--ISNUMBER(SEARCH({{"0","1","2","3","4","5","6","7","8","9"}},B{r})))>0,"igen","nem"))'),
        14: lambda r: (f'=IF(B{r}="","",TRIM('
                       f'IF(K{r}=0,"nincs »kell« (cél? tény?); ","")&'
                       f'IF(K{r}>1,"több »kell«: bontsd szét; ","")&'
                       f'IF(L{r}>0,"kétértelmű kifejezés; ","")&'
                       f'IF(OR(LEFT(LOWER(B{r}),11)="az operátor",LEFT(LOWER(B{r}),13)="a felhasználó",LEFT(LOWER(B{r}),12)="a karbantart"),"működési leírás? (az alany nem a rendszer); ","")&'
                       f'IF(ISNUMBER(SEARCH("TBD",B{r})),"TBD helyett becslés + TBR; ","")&'
                       f'IF(M{r}="nem","nincs számérték – mérhető?; ","")&'
                       f'IF(D{r}="","hiányzó indoklás; ","")&'
                       f'IF(E{r}="","hiányzó forrás; ","")&'
                       f'IF(G{r}="","hiányzó verifikációs mód; ","")&'
                       f'IF(H{r}="","nincs felelős; ","")))'),
    }


def reg_lap(wb, nev, adatok, ures, utolso_szotar):
    ws = wb.create_sheet(nev)
    cimsor(ws, "Követelménynyilvántartás", "Az utolsó négy oszlop automatikus ellenőrzés; üres „Ellenőrzés” cella = nem talált hibát.")
    u = tablazat(ws, 4, FEJ, SZEL, adatok, bemeneti_oszlopok=range(1, 11), kepletek=kepletek(utolso_szotar), uressor=ures)
    legordulo(ws, f"C5:C{u}", TIPUS)
    legordulo(ws, f"F5:F{u}", PRIOR)
    legordulo(ws, f"G5:G{u}", VERIF)
    legordulo(ws, f"I5:I{u}", ALLAPOT)
    legordulo(ws, f"J5:J{u}", ["igen", "nem"])
    megjegyzes(ws["J4"], "KDR: kulcsfontosságú, meghatározó követelmény (prioritásától függetlenül nagy hatással van a tervre, a költségre vagy az ütemtervre).")
    megjegyzes(ws["L4"], "A Szótár lap kétértelmű kifejezéseinek előfordulása. A szótár bővíthető.")
    ws.freeze_panes = "C5"
    return ws, u


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Követelménynyilvántartás – sablon", [
        "■ Mire való? A rendszerkövetelmények egységes rögzítése attribútumokkal, és a megfogalmazási hibák automatikus jelzése.",
        "1. Egy sor egy követelmény. A szöveg „A ‹rendszer›nek … kell …” szerkezetű legyen, egyetlen „kell”-lel, mértékkel és értékkel.",
        "2. Töltsd ki az attribútumokat: típus, indoklás, forrás (melyik elvárásból, szabványból vagy felsőbb követelményből), prioritás, verifikációs mód, felelős, állapot, KDR.",
        "3. Az „Ellenőrzés” oszlop jelzi a tipikus hibákat (nincs vagy több „kell”, kétértelmű kifejezés, TBD, hiányzó attribútum). A jelzés figyelmeztetés: a döntés a tiéd.",
        "4. A „Szótár” lapon bővítheted a kétértelmű kifejezések listáját.",
        "5. Az „Összesítés” lap típus és verifikációs mód szerint számol, és megadja a jelzett sorok számát.",
        "■ Példa: a „Példa – KoboCella” lap jó és (R-30-tól) szándékosan hibás követelményeket is tartalmaz.",
    ])
    regi = wb.active
    ws_s = wb.create_sheet("Szótár")
    cimsor(ws_s, "Kétértelmű kifejezések", "Bővíthető lista; a követelményekben való előfordulásukat a nyilvántartás jelzi.")
    fejlec(ws_s, 4, ["Kifejezés"], [28])
    for i, sz in enumerate(SZOTAR + [None] * 16, start=5):
        bemenet(ws_s.cell(row=i, column=1), sz)
    utolso_sz = 4 + len(SZOTAR) + 16
    reg_lap(wb, "Nyilvántartás", [], 80, utolso_sz)
    ws_p, u = reg_lap(wb, "Példa – KoboCella", PELDA, 5, utolso_sz)
    # összesítés
    ws = wb.create_sheet("Összesítés")
    cimsor(ws, "Összesítés", "A „Nyilvántartás” lapra vonatkozik; a B oszlop képletében a lapnév átírható a példalapra.")
    fejlec(ws, 4, ["Típus", "Darab"], [22, 10])
    rng = "Nyilvántartás!$C$5:$C$84"
    for i, t in enumerate(TIPUS, start=5):
        szoveg(ws.cell(row=i, column=1), t)
        keplet(ws.cell(row=i, column=2), f"=COUNTIF({rng},A{i})")
    fejlec(ws, 4, ["Verifikációs mód", "Darab"], [20, 10], oszlop=4)
    for i, v in enumerate(VERIF, start=5):
        szoveg(ws.cell(row=i, column=4), v)
        keplet(ws.cell(row=i, column=5), f"=COUNTIF(Nyilvántartás!$G$5:$G$84,D{i})")
    szoveg(ws.cell(row=11, column=4), "Követelmények száma", felkov=True)
    keplet(ws.cell(row=11, column=5), '=COUNTIF(Nyilvántartás!$B$5:$B$84,"?*")', felkov=True)
    szoveg(ws.cell(row=12, column=4), "Ebből jelzett sor", felkov=True)
    keplet(ws.cell(row=12, column=5), '=SUMPRODUCT((Nyilvántartás!$B$5:$B$84<>"")*(LEN(Nyilvántartás!$N$5:$N$84)>0))', felkov=True)
    szoveg(ws.cell(row=13, column=4), "KDR-ek száma", felkov=True)
    keplet(ws.cell(row=13, column=5), '=COUNTIF(Nyilvántartás!$J$5:$J$84,"igen")', felkov=True)
    wb.move_sheet("Szótár", offset=3)
    return mentes(wb, "kovetelmeny_sablon.xlsx")


if __name__ == "__main__":
    keszit()
