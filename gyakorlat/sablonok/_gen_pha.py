"""Előzetes veszélyelemzés (PHA) energia–gát szemlélettel (eszközlap: PHA)."""
from _kozos import *  # noqa: F401,F403
from _skalak import matrix_racs, skala_lap, zona, zona_szinezes

ENERGIA = [
    ("mozgási (mechanikai)", "mozgó gépelemek, robotkar, forgó orsó, jármű, szállítószalag"),
    ("helyzeti (gravitációs)", "emelt teher, magasban végzett munka, leeső alkatrész"),
    ("nyomás, rugalmas", "sűrített levegő, hidraulika, feszített rugó, nyomástartó edény"),
    ("villamos", "hálózati feszültség, akkumulátor, kondenzátor, statikus feltöltődés"),
    ("hő", "forró felület, hegesztés, fűtés, hűtőközeg"),
    ("kémiai", "lítiumion-akkumulátor, oldószer, kenőanyag, éghető anyag"),
    ("sugárzás", "lézer, UV, röntgen, elektromágneses tér"),
    ("akusztikus, rezgés", "zaj, kéziszerszám-rezgés, egésztest-rezgés"),
    ("ergonómiai terhelés", "ismétlődő mozdulat, kényszertartás, emelés"),
    ("vezérlés, szoftver", "váratlan indulás, hibás vezérlési parancs, kiesett felügyelet"),
    ("biológiai, környezeti", "por, penész, szélsőséges időjárás"),
]
PHA = [  # id, alrendszer, energia, veszély, ok, célpont, következmény, S0, P0, intézkedés, típus, S1, P1, indoklás, verifikáció
    ("H1", "kobot", "mozgási (mechanikai)", "a kobotkar ütközése a kezelővel", "a kezelő a közös térben van, miközben a kar mozog", "személy", "zúzódás, törés",
     3, 4, "erő- és teljesítményhatárolás; sebesség- és távolságfelügyelet lézerszkennerrel; legfeljebb 250 mm/s a közös térben (R-11)", 2, 2, 3, "",
     "a biztonsági funkciók validálása, ütközési erőmérés"),
    ("H2", "befogó", "nyomás, rugalmas", "kéz becsípődése a befogó és a fedél között", "a kezelő keze a befogóban van záráskor", "személy", "ujjzúzódás, törés",
     4, 3, "a befogó csak zónaelhagyás után zár; korlátozott szorítóerő", 1, 3, 2, "", "funkcionális teszt, szorítóerő-mérés"),
    ("H3", "csavarozó egység", "mozgási (mechanikai)", "ruha vagy kesztyű behúzása a forgó orsóba", "az orsó indul, miközben a kéz a közelében van", "személy", "ujj- és kézsérülés",
     3, 3, "burkolat; az orsó csak zónaelhagyás után indul", 2, 3, 1, "", "szemrevételezés, funkcionális teszt"),
    ("H4", "vezérlőszekrény", "villamos", "áramütés", "feszültség alatti rész karbantartáskor", "személy", "halálos áramütés",
     5, 2, "érintésvédelem; kizárási eljárás; csak képzett villamos szakember dolgozhat", 2, 5, 1,
     "a súlyosság nem csökkenthető; a karbantartás ritka, a szakemberek képzettek, a kizárás bevett gyakorlat: a további csökkentés aránytalan", "az eljárás éves auditja"),
    ("H5", "munkahely", "ergonómiai terhelés", "ismétlődő törzshajlítás", "nem megfelelő munkamagasság", "személy", "mozgásszervi panaszok",
     3, 5, "a kezelőhöz állítható munkamagasság; legfeljebb 20° törzshajlítás (R-05)", 1, 2, 3, "", "ergonómiai mérés (R-05 verifikációja)"),
    ("H6", "cellavezérlés", "vezérlés, szoftver", "váratlan indulás", "szoftverhiba a cellavezérlőben", "személy", "ütközés, becsípődés",
     4, 2, "a zónafelügyelet független biztonsági vezérlésen fut", 1, 4, 1, "", "a biztonsági vezérlés validálása"),
    ("H7", "anyagellátás", "helyzeti (gravitációs)", "leeső motorház", "a motorház kicsúszik a kézből", "személy", "lábsérülés",
     2, 3, "csúszásgátló tálca; munkavédelmi lábbeli", 3, 2, 2, "", "bejárás"),
    ("H8", "befogó pneumatika", "nyomás, rugalmas", "levegőtömlő leválása", "a gyorscsatlakozó kioldódik", "személy", "arc- és szemsérülés",
     3, 2, "biztosított gyorscsatlakozók; tömlőrögzítés", 2, 3, 1, "", "nyomáspróba, szemrevételezés"),
]
N = 40


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Előzetes veszélyelemzés (PHA) – sablon", [
        "■ Mire való? A veszélyek korai leltára a fejlesztés koncepciószakaszában: energiaforrások, célpontok, kockázat, ellenintézkedések és maradó kockázat (Ericson, 2015; kézikönyv 14. fejezet).",
        "1. Az „Energiaforrások” lapon jelöld, mely energiafajták vannak jelen a rendszerben, és hol. Ez a veszélyazonosítás vezérfonala.",
        "2. A „PHA” lapon soronként egy veszély: alrendszer, energiaforrás, veszély, kiváltó ok, célpont (személy, berendezés, termék, környezet), következmény, kiinduló súlyosság (S) és valószínűség (P).",
        "3. Írd le az ellenintézkedést, és jelöld a típusát az ISO 12100 sorrendje szerint: 1 eredendően biztonságos tervezés, 2 műszaki védőintézkedés, 3 használati információ (figyelmeztetés, képzés, egyéni védőeszköz).",
        "4. Add meg a maradó S-t és P-t. Ha a maradó kockázat az ALARP-tartományban van, írd le az indoklást, miért nem észszerű a további csökkentés.",
        "5. Minden intézkedéshez rendelj verifikációs módot; ezek a verifikációs terv elemei lesznek.",
        "■ Példa: a KoboCella előzetes veszélyelemzése (kézikönyv 14. fejezet).",
    ])
    skala_lap(wb)
    e = wb.create_sheet("Energiaforrások")
    cimsor(e, "Energiaforrás-ellenőrzőlista (Haddon, 1973 és Ericson, 2015 alapján)")
    tablazat(e, 3, ["Energiafajta", "Példák", "Jelen van? (igen/nem)", "Hol a rendszerben?"], [26, 60, 14, 50],
             [[a, b, ("igen" if a in {p[2] for p in PHA} else "nem"), ""] for a, b in ENERGIA], bemeneti_oszlopok=(3, 4))
    legordulo(e, f"C4:C{3 + len(ENERGIA)}", ["igen", "nem"])
    ws = wb.create_sheet("PHA")
    cimsor(ws, "Előzetes veszélyelemzés", "Intézkedéstípus: 1 eredendően biztonságos tervezés, 2 műszaki védőintézkedés, 3 használati információ.")
    fej = ["Azonosító", "Alrendszer, tevékenység", "Energiaforrás", "Veszély", "Kiváltó ok", "Célpont", "Következmény", "S", "P", "Zóna",
           "Ellenintézkedés", "Típus (1–3)", "S maradó", "P maradó", "Zóna maradó", "ALARP-indoklás", "Verifikáció", "Jelzés"]
    sor = [[a, b, c, d, e_, f, g, h, i, None, j, k, l, m, None, n, o, None] for a, b, c, d, e_, f, g, h, i, j, k, l, m, n, o in PHA]
    kepl = {10: lambda r: zona(f"H{r}", f"I{r}"), 15: lambda r: zona(f"M{r}", f"N{r}"),
            18: lambda r: (f'=IF(D{r}="","",IF(O{r}="elfogadhatatlan","további intézkedés kell",IF(AND(O{r}="ALARP",P{r}=""),"ALARP-indoklás hiányzik",'
                           f'IF(AND(H{r}>=4,L{r}=3),"súlyos veszélynél a tájékoztatás nem elég",IF(Q{r}="","verifikáció hiányzik","")))))')}
    u = tablazat(ws, 4, fej, [8, 16, 20, 30, 30, 10, 20, 5, 5, 14, 46, 8, 7, 7, 14, 40, 28, 30], sor,
                 bemeneti_oszlopok=(1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17), kepletek=kepl, uressor=N - len(sor))
    for r in range(5, u + 1):
        for c in (8, 9, 10, 12, 13, 14, 15):
            ws.cell(row=r, column=c).alignment = kozep
    zona_szinezes(ws, f"J5:J{u}", "J5"); zona_szinezes(ws, f"O5:O{u}", "O5")
    legordulo(ws, f"C5:C{u}", [a for a, _ in ENERGIA])
    legordulo(ws, f"F5:F{u}", ["személy", "berendezés", "termék", "környezet"])
    legordulo(ws, f"L5:L{u}", ["1", "2", "3"])
    for rg in (f"H5:I{u}", f"M5:N{u}"):
        legordulo(ws, rg, ["1", "2", "3", "4", "5"])
    ws.freeze_panes = "E5"
    o = wb.create_sheet("Összesítés")
    cimsor(o, "Összesítés")
    matrix_racs(o, 3, 1, "Kiinduló kockázat", f"PHA!$H$5:$H${u}", f"PHA!$I$5:$I${u}")
    matrix_racs(o, 3, 8, "Maradó kockázat", f"PHA!$M$5:$M${u}", f"PHA!$N$5:$N${u}")
    fejlec(o, 12, ["Mutató", "Érték"], [44, 14])
    for k_, (t, f) in enumerate([
            ("Veszélyek száma", f'=COUNTA(D5:D{u})'.replace("D5", "PHA!D5")),
            ("Kiinduló: elfogadhatatlan / ALARP / elfogadható", f'=COUNTIF(PHA!J5:J{u},"elfogadhatatlan")&" / "&COUNTIF(PHA!J5:J{u},"ALARP")&" / "&COUNTIF(PHA!J5:J{u},"elfogadható")'),
            ("Maradó: elfogadhatatlan / ALARP / elfogadható", f'=COUNTIF(PHA!O5:O{u},"elfogadhatatlan")&" / "&COUNTIF(PHA!O5:O{u},"ALARP")&" / "&COUNTIF(PHA!O5:O{u},"elfogadható")'),
            ("Intézkedések: tervezési / műszaki védő / tájékoztató", f'=COUNTIF(PHA!L5:L{u},1)&" / "&COUNTIF(PHA!L5:L{u},2)&" / "&COUNTIF(PHA!L5:L{u},3)'),
            ("Jelzések száma", f'=COUNTIF(PHA!R5:R{u},"?*")')]):
        szoveg(o.cell(row=13 + k_, column=1), t)
        keplet(o.cell(row=13 + k_, column=2), f, None, True)
    o.column_dimensions["A"].width = 44
    return mentes(wb, "pha_sablon.xlsx")
