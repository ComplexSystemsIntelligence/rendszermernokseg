"""Kockázati mátrix és kockázati nyilvántartás (eszközlap: Kockázati mátrix)."""
from _kozos import *  # noqa: F401,F403
from _skalak import matrix_racs, skala_lap, zona, zona_szinezes

KOCK = [  # id, állítás, kategória, felelős, S0, P0, kezelés, intézkedés, S1, P1, küszöb, állapot
    ("K1", "Mivel a régi gépek egy részének nincs digitális interfésze, fennáll a lehetősége, hogy a gépi adatgyűjtés csak kiegészítő hardverrel oldható meg, ami az első ütemet 2–3 hónappal késlelteti.",
     "ütemezési", "projektvezető", 3, 4, "csökkentés", "a gépek felmérése szerződéskötés előtt; kiegészítő hardver beárazása tartalékként", 3, 2, "a felmérés 3-nál több interfész nélküli gépet talál", "figyelt"),
    ("K2", "Mivel a sürgős rendelések előresorolása eddig szóban történt, fennáll a lehetősége, hogy a műszakvezetők megkerülik az ütemezőt, így a határidő-teljesítés nem javul.",
     "technikai", "termelésvezető", 4, 3, "csökkentés", "műszakvezetők bevonása a szabályok kialakításába; az átsorolás naplózása; napi áttekintés", 3, 2, "a rendszeren kívüli átsorolások aránya 10% fölött", "nyitott"),
    ("K3", "Mivel a platformot egyetlen beszállító fejleszti, fennáll a lehetősége, hogy a későbbi ütemek ára vagy ütemezése a beszállító helyzetétől függ.",
     "költség", "ügyvezető", 4, 2, "megosztás", "nyílt adatexport; a második ütem árának rögzítése a keretszerződésben", 3, 2, "a beszállító ármódosítást jelez", "figyelt"),
    ("K4", "Mivel a technológiai normaidők egy része elavult, fennáll a lehetősége, hogy az ütemező javaslatai pontatlanok, és a műszakvezetők elveszítik a bizalmukat a rendszerben.",
     "technikai", "technológus", 3, 4, "csökkentés", "a 20 leggyakoribb termék normaidejének felülvizsgálata a gépi adatokkal az indulás előtt", 2, 2, "a tervezett és a tényleges idő eltérése 15% fölött", "nyitott"),
    ("K5", "Mivel a csarnok vezeték nélküli lefedettsége egyenetlen, fennáll a lehetősége, hogy a gépi adatok egy része elvész.",
     "technikai", "informatikus", 2, 3, "csökkentés", "helyszíni felmérés; vezetékes bekötés a lefedetlen gépeknél", 2, 1, "adatvesztés 1% fölött", "lezárt"),
    ("K6", "Mivel a termelésvezető a napi termelés irányítása mellett kulcsfelhasználó is, fennáll a lehetősége, hogy a bevezetési feladatok késnek.",
     "ütemezési", "ügyvezető", 3, 3, "csökkentés", "helyettes kijelölése a napi irányításra a bevezetés idejére", 3, 2, "két egymást követő mérföldkő csúszása", "figyelt"),
    ("K7", "Mivel a gépeket hálózatra kötjük, fennáll a lehetősége, hogy egy kibertámadás leállítja a termelést.",
     "technikai", "informatikus", 4, 2, "csökkentés", "hálózati szegmentálás; a gépi hálózat elkülönítése az irodaitól; mentési rend", 4, 1, "biztonsági esemény a gépi hálózaton", "figyelt"),
    ("K8", "Mivel az integráció a meglévő vállalatirányítási rendszerrel még nem ismert részletességű, fennáll a lehetősége, hogy az első ütem költsége túllépi a keretet.",
     "költség", "projektvezető", 3, 3, "csökkentés", "integrációs prototípus az első hónapban; rögzített árú integrációs munkacsomag", 3, 2, "a prototípus 20%-nál nagyobb többletmunkát mutat", "nyitott"),
]
HONAP = ["M0", "M1", "M2", "M3", "M4", "M5", "M6"]
KOVETES = {"K1": [12, 12, 9, 6, 6, 6, 6], "K2": [12, 12, 12, 12, 9, 6, 6], "K3": [8, 8, 6, 6, 6, 6, 6], "K4": [12, 9, 9, 6, 4, 4, 4],
           "K5": [6, 6, 3, 2, 2, 2, 2], "K6": [9, 9, 9, 6, 6, 6, 6], "K7": [8, 8, 8, 4, 4, 4, 4], "K8": [9, 9, 9, 9, 6, 6, 6]}
TERV = [76, 70, 63, 57, 51, 44, 38]
N = 30


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Kockázati mátrix és kockázati nyilvántartás – sablon", [
        "■ Mire való? A kockázatok egységes minősítése valószínűség és súlyosság alapján, a kezelés tervezése és a kockázatok követése a projekt során (kézikönyv 14. fejezet).",
        "1. A „Skálák” lapon igazítsd a súlyossági és valószínűségi kategóriákat a projekthez. A szomszédos valószínűségi szintek nagyságrendben különbözzenek. Kalibráld a mátrixot egy mindenki által ismert forgatókönyvvel, és a zónahatárokat a vezetéssel hagyasd jóvá.",
        "2. A „Nyilvántartás” lapon minden kockázatot feltétel–következmény formában írj le: „Mivel [ma igaz feltétel], fennáll a lehetősége, hogy [esemény], ami [következmény]”.",
        "3. Add meg a kiinduló súlyosságot (S) és valószínűséget (P), a kezelés módját, az intézkedést, a várható maradó S-t és P-t, a beavatkozást kiváltó küszöböt és az állapotot. A zónát a lap számolja.",
        "4. A „Mátrix” lap a kockázatok számát mutatja a cellákban, a kezelés előtt és után.",
        "5. A „Követés” lapon havonta rögzítsd a kockázatok aktuális pontszámát (S × P), és vesd össze a tervezett csökkenéssel.",
        "■ Példa: a ForgácsTech MES-bevezetésének projektkockázatai (kézikönyv 14. fejezet).",
    ])
    skala_lap(wb)
    ws = wb.create_sheet("Nyilvántartás")
    cimsor(ws, "Kockázati nyilvántartás", "S: súlyosság (következmény), P: valószínűség, 1–5. A pontszám S × P, a zóna az S + P küszöbök szerint.")
    fej = ["Azonosító", "Kockázati állítás (feltétel → esemény → következmény)", "Kategória", "Felelős", "S kiinduló", "P kiinduló",
           "Pontszám", "Zóna", "Kezelés", "Intézkedés", "S maradó", "P maradó", "Pontszám maradó", "Zóna maradó", "Beavatkozási küszöb", "Állapot"]
    sor = [[a, b, c, d, e, f, None, None, g, h, i, j, None, None, k, l] for a, b, c, d, e, f, g, h, i, j, k, l in KOCK]
    kepl = {7: lambda r: f'=IF(OR(E{r}="",F{r}=""),"",E{r}*F{r})', 8: lambda r: zona(f"E{r}", f"F{r}"),
            13: lambda r: f'=IF(OR(K{r}="",L{r}=""),"",K{r}*L{r})', 14: lambda r: zona(f"K{r}", f"L{r}")}
    u = tablazat(ws, 4, fej, [9, 60, 12, 14, 8, 8, 9, 15, 12, 44, 8, 8, 9, 15, 34, 12], sor,
                 bemeneti_oszlopok=(1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 15, 16), kepletek=kepl, uressor=N - len(sor))
    for r in range(5, u + 1):
        for c in (5, 6, 7, 8, 11, 12, 13, 14):
            ws.cell(row=r, column=c).alignment = kozep
    zona_szinezes(ws, f"H5:H{u}", "H5"); zona_szinezes(ws, f"N5:N{u}", "N5")
    legordulo(ws, f"C5:C{u}", ["biztonsági", "technikai", "költség", "ütemezési", "egyéb"])
    legordulo(ws, f"I5:I{u}", ["elkerülés", "forrás megszüntetése", "csökkentés", "megosztás", "vállalás"])
    legordulo(ws, f"P5:P{u}", ["nyitott", "figyelt", "bekövetkezett", "lezárt"])
    for rg in (f"E5:F{u}", f"K5:L{u}"):
        legordulo(ws, rg, ["1", "2", "3", "4", "5"])
    rr = u + 2
    for k_, (t, f, fmt) in enumerate([
            ("Kockázatok száma", f'=COUNTA(A5:A{u})', "0"),
            ("Elfogadhatatlan / ALARP / elfogadható (kiinduló)", f'=COUNTIF(H5:H{u},"elfogadhatatlan")&" / "&COUNTIF(H5:H{u},"ALARP")&" / "&COUNTIF(H5:H{u},"elfogadható")', None),
            ("Elfogadhatatlan / ALARP / elfogadható (maradó)", f'=COUNTIF(N5:N{u},"elfogadhatatlan")&" / "&COUNTIF(N5:N{u},"ALARP")&" / "&COUNTIF(N5:N{u},"elfogadható")', None),
            ("Összpontszám kiinduló → maradó", f'=SUM(G5:G{u})&" → "&SUM(M5:M{u})', None)]):
        szoveg(ws.cell(row=rr + k_, column=2), t, felkov=True)
        keplet(ws.cell(row=rr + k_, column=3), f, fmt, True)
        ws.merge_cells(start_row=rr + k_, start_column=3, end_row=rr + k_, end_column=6)
    ws.freeze_panes = "C5"
    m = wb.create_sheet("Mátrix")
    cimsor(m, "Kockázati mátrix: a kockázatok száma cellánként", "A színek a „Skálák” lap zónahatárait követik.")
    matrix_racs(m, 4, 1, "Kezelés előtt", f"Nyilvántartás!$E$5:$E${u}", f"Nyilvántartás!$F$5:$F${u}")
    matrix_racs(m, 4, 8, "Kezelés után (maradó)", f"Nyilvántartás!$K$5:$K${u}", f"Nyilvántartás!$L$5:$L${u}")
    szoveg(m["A13"], "Függőleges tengely: súlyosság (S), vízszintes: valószínűség (P).")
    kv = wb.create_sheet("Követés")
    cimsor(kv, "A kockázatok pontszámának (S × P) havi követése")
    fejlec(kv, 4, ["Azonosító"] + HONAP, [11] + [8] * len(HONAP))
    for i in range(N):
        r = 5 + i
        keplet(kv.cell(row=r, column=1), f'=IF(Nyilvántartás!A{5 + i}="","",Nyilvántartás!A{5 + i})')
        ert = KOVETES.get(KOCK[i][0]) if i < len(KOCK) else None
        for j in range(len(HONAP)):
            bemenet(kv.cell(row=r, column=2 + j), ert[j] if ert else None)
    rt, rp = 5 + N, 6 + N
    szoveg(kv.cell(row=rt, column=1), "Összesen", felkov=True)
    szoveg(kv.cell(row=rp, column=1), "Terv", felkov=True)
    for j in range(len(HONAP)):
        col = get_column_letter(2 + j)
        keplet(kv.cell(row=rt, column=2 + j), f"=SUM({col}5:{col}{4 + N})", "0", True)
        bemenet(kv.cell(row=rp, column=2 + j), TERV[j])
    ch = LineChart()
    ch.add_data(Reference(kv, min_col=1, max_col=1 + len(HONAP), min_row=rt, max_row=rp), from_rows=True, titles_from_data=True)
    ch.set_categories(Reference(kv, min_col=2, max_col=1 + len(HONAP), min_row=4))
    diagram_kozos(ch, "Összes kockázati pontszám: tény és terv", "hónap", "Σ S × P", 18, 8)
    kv.add_chart(ch, f"J4")
    return mentes(wb, "kockazati_matrix_sablon.xlsx")
