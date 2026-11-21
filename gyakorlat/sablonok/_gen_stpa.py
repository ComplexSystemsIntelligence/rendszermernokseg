"""STPA – rendszerelméleti folyamatelemzés (eszközlap: STPA)."""
from _kozos import *  # noqa: F401,F403

VESZTESEG = [("L1", "a kezelő megsérül"), ("L2", "hibás motor jut a vevőhöz"), ("L3", "a termelés kiesik, a szállítás késik")]
VESZELY = [("H1", "a kobot a kezelő közelében a biztonságos határt meghaladó sebességgel vagy erővel mozog", "L1"),
           ("H2", "hibás kötésű motor hagyja el a cellát", "L2"),
           ("H3", "a cella ok nélkül áll, vagy indokolatlanul leromlott üzemben marad", "L3")]
KORLAT = [("SC1", "ha a kezelő a közös térben van, a kobot sebessége és ereje nem lépheti túl a határértéket", "H1"),
          ("SC2", "hibás kötésű motor nem kerülhet a kiadóba", "H2"),
          ("SC3", "a cella csak indokolt esetben álljon le, és a leromlott üzemből a lehető leghamarabb térjen vissza", "H3")]
ELEMEK = [("MES", "termelésirányítás, MES", "irányító", 1), ("KE", "kezelő", "irányító", 2), ("CV", "cellavezérlő", "irányító", 2),
          ("BV", "biztonsági vezérlés", "irányító", 2), ("SZ", "lézerszkenner", "érzékelő", 3), ("FO", "kobot, csavarozó, befogó", "szabályozott folyamat", 4)]
KAPCS = [("MES", "CV", "beavatkozás", "rendelés, típusprogram"), ("CV", "MES", "visszacsatolás", "gyártási adatok"),
         ("CV", "FO", "beavatkozás", "ciklus indítása, mozgásparancsok"), ("FO", "CV", "visszacsatolás", "nyomaték, állapot"),
         ("BV", "FO", "beavatkozás", "sebességkorlát, biztonsági leállítás"), ("BV", "CV", "visszacsatolás", "biztonsági állapot"),
         ("KE", "CV", "beavatkozás", "nyugtázás, indítás"), ("CV", "KE", "visszacsatolás", "HMI-jelzések"),
         ("KE", "FO", "beavatkozás", "vészleállítás, alkatrész behelyezése"), ("FO", "SZ", "visszacsatolás", "a kezelő helyzete"),
         ("SZ", "BV", "visszacsatolás", "zónajel")]
BEAVATKOZAS = [("CA1", "teljes sebesség engedélyezése", "BV", "FO"), ("CA2", "ciklus indítása", "CV", "FO"),
               ("CA3", "nyugtázás", "KE", "CV"), ("CA4", "vészleállítás", "KE", "FO")]
TIPUSOK = ["nem adja ki", "kiadja", "túl korán / későn / rossz sorrendben", "túl sokáig / túl korán leáll"]
UCA = [("U1", "CA1", "kiadja", "a teljes sebességet engedélyezi, miközben a kezelő a közös térben van", "H1"),
       ("U2", "CA1", "túl korán / későn / rossz sorrendben", "a teljes sebességet azelőtt engedélyezi, hogy a kezelő teljesen elhagyta a zónát", "H1"),
       ("U3", "CA1", "túl sokáig / túl korán leáll", "a kezelő belépése után is fenntartja a teljes sebességet", "H1"),
       ("U4", "CA1", "nem adja ki", "tartósan nem engedélyezi a teljes sebességet, pedig a zóna üres", "H3"),
       ("U5", "CA2", "kiadja", "a ciklust indítja, miközben a fedél nincs a helyén", "H2"),
       ("U6", "CA2", "túl korán / későn / rossz sorrendben", "a ciklust a kezelő kezének kilépése előtt indítja", "H1"),
       ("U7", "CA3", "kiadja", "nyugtáz, amikor a hibás darab még nincs a selejtdobozban", "H2"),
       ("U8", "CA4", "nem adja ki", "vészhelyzetben nem állítja le a cellát", "H1"),
       ("U9", "CA4", "túl korán / későn / rossz sorrendben", "a vészleállítást túl későn adja ki", "H1")]
FORG = [("F1", "U1", "hibás folyamatmodell", "a szkenner védőmezeje karbantartás után rosszul van visszaállítva; a biztonsági vezérlés szerint a zóna üres",
         "a mezőkonfiguráció ellenőrzése; napi indítási próba (FMEA F7)"),
        ("F2", "U1", "hiányzó vagy hibás visszacsatolás", "a kezelő a tálcaállvány takarásából lép be, a szkenner nem látja",
         "az elrendezés módosítása, takarásmentes belépési irányok"),
        ("F3", "U2", "a beavatkozás hatása késik", "a szkenner reakcióideje és a kobot fékútja nagyobb a tervezettnél",
         "reakcióidő- és fékútmérés a verifikációban"),
        ("F4", "U7", "emberi tényező: rutin, helyzettudatosság", "a nyugtázás a mozdulatsor része lett, a kezelő nem olvassa el a jelzést",
         "nyugtázás helyett fizikai cselekvés; selejtdoboz-érzékelő"),
        ("F5", "U5", "hiányzó vagy hibás visszacsatolás", "a fedél jelenlétét csak a kezelő ellenőrzi", "befogóérzékelő a fedélre"),
        ("F6", "U8", "elrendezés, eljárás", "a vészleállító a kezelő munkahelyéről nem érhető el", "második vészleállító a munkahelyen"),
        ("F7", "U6", "hibás algoritmus vagy eljárás", "az indítás egy gombnyomás, miközben a kezelő másik keze még a befogóban lehet",
         "indítás csak a zóna elhagyása után (a szkenner jelére)"),
        ("F8", "U9", "emberi tényező: rutin, helyzettudatosság", "a kezelő nem ismeri fel időben a veszélyt, mert a kobot mozgása kiszámíthatatlannak tűnik",
         "a kobot következő mozgásának jelzése a HMI-n; az automatikus védelmek nem a kezelő reakciójára épülnek")]
OKOK = ["hibás folyamatmodell", "hiányzó vagy hibás visszacsatolás", "hibás algoritmus vagy eljárás", "a beavatkozás nem hajtódik végre",
        "a beavatkozás hatása késik", "emberi tényező: rutin, helyzettudatosság", "elrendezés, eljárás", "kommunikációs hiba", "egyéb"]


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "STPA – rendszerelméleti folyamatelemzés – sablon", [
        "■ Mire való? A biztonság irányítási problémaként való elemzése: mely beavatkozások (control actions) lehetnek veszélyesek, és miért adhatja ki őket egy irányító (ember, szoftver, szervezet) – Leveson és Thomas STPA-kézikönyve szerint (kézikönyv 17. fejezet).",
        "1. A „Cél” lapon rögzítsd a veszteségeket (L), a rendszerszintű veszélyeket (H, a kapcsolódó veszteséggel) és a biztonsági korlátokat (SC, a kapcsolódó veszéllyel).",
        "2. Az „Irányítási struktúra” lapon sorold fel az elemeket (irányító, érzékelő, beavatkozó, szabályozott folyamat, szint) és a kapcsolatokat (beavatkozás lefelé, visszacsatolás felfelé).",
        "3. A „Beavatkozások” lapon add meg a vizsgált beavatkozásokat. Az „UCA” lapon mindegyiknél vizsgáld meg a négy típust: nem adja ki; kiadja; túl korán, túl későn vagy rossz sorrendben; túl sokáig tart vagy túl korán áll le. Ami veszélyes, az nem biztonságos beavatkozás (UCA), a kapcsolódó veszéllyel.",
        "4. A „Forgatókönyvek” lapon minden UCA-hoz keresd meg, miért adhatja ki az irányító (hibás folyamatmodell, hiányzó visszacsatolás, hibás eljárás stb.), és milyen követelmény vagy intézkedés zárja ki.",
        "5. Az „Összesítés” lap mutatja a lefedettséget: melyik beavatkozás melyik típusát vizsgáltad, mely veszélyhez nincs UCA, mely UCA-hoz nincs forgatókönyv.",
        "■ Példa: a KoboCella cellairányítása (kézikönyv 17. fejezet).",
    ])
    c = wb.create_sheet("Cél")
    cimsor(c, "Veszteségek, veszélyek, biztonsági korlátok")
    tablazat(c, 3, ["Veszteség", "Leírás"], [10, 70], [list(x) for x in VESZTESEG], bemeneti_oszlopok=(1, 2), uressor=7)
    szoveg(c["A15"], "Rendszerszintű veszélyek", felkov=True)
    uh = tablazat(c, 16, ["Veszély", "Leírás (a rendszer állapota)", "Veszteség(ek)", "Ellenőrzés"], [10, 70, 14, 30],
                  [list(x) + [None] for x in VESZELY], bemeneti_oszlopok=(1, 2, 3),
                  kepletek={4: lambda r: f'=IF(A{r}="","",IF(COUNTIF($A$4:$A$13,C{r})=0,"ismeretlen veszteség",""))'}, uressor=7)
    szoveg(c[f"A{uh + 2}"], "Biztonsági korlátok", felkov=True)
    tablazat(c, uh + 3, ["Korlát", "Leírás", "Veszély(ek)"], [10, 70, 14], [list(x) for x in KORLAT], bemeneti_oszlopok=(1, 2, 3), uressor=7)
    s = wb.create_sheet("Irányítási struktúra")
    cimsor(s, "Az irányítási struktúra", "Szint: 1 a legfelső irányító; a szabályozott folyamat a legalsó szint.")
    ue = tablazat(s, 3, ["Elem", "Megnevezés", "Típus", "Szint"], [10, 34, 22, 8], [list(x) for x in ELEMEK], bemeneti_oszlopok=(1, 2, 3, 4), uressor=9)
    legordulo(s, f"C4:C{ue}", ["irányító", "érzékelő", "beavatkozó", "szabályozott folyamat"])
    szoveg(s[f"A{ue + 2}"], "Kapcsolatok", felkov=True)
    uk = tablazat(s, ue + 3, ["Honnan", "Hová", "Típus", "Megnevezés", "Ellenőrzés"], [10, 10, 16, 40, 24], [list(x) + [None] for x in KAPCS],
                  bemeneti_oszlopok=(1, 2, 3, 4), uressor=14,
                  kepletek={5: lambda r: f'=IF(A{r}="","",IF(OR(COUNTIF($A$4:$A${ue},A{r})=0,COUNTIF($A$4:$A${ue},B{r})=0),"ismeretlen elem",""))'})
    legordulo(s, f"C{ue + 4}:C{uk}", ["beavatkozás", "visszacsatolás"])
    b = wb.create_sheet("Beavatkozások")
    cimsor(b, "Vizsgált beavatkozások (control actions)")
    ub = tablazat(b, 3, ["Azonosító", "Beavatkozás", "Irányító", "Cél"], [11, 40, 12, 12], [list(x) for x in BEAVATKOZAS], bemeneti_oszlopok=(1, 2, 3, 4), uressor=11)
    u = wb.create_sheet("UCA")
    cimsor(u, "Nem biztonságos beavatkozások (UCA)", "Típus: a négy STPA-kérdés. A kontextus (mikor veszélyes) a leírás része.")
    uu = tablazat(u, 3, ["UCA", "Beavatkozás", "Típus", "Leírás (kontextussal)", "Veszély", "Ellenőrzés"], [8, 12, 30, 70, 10, 30],
                  [list(x) + [None] for x in UCA], bemeneti_oszlopok=(1, 2, 3, 4, 5), uressor=31,
                  kepletek={6: lambda r: (f'=IF(A{r}="","",IF(COUNTIF(Beavatkozások!$A$4:$A${ub},B{r})=0,"ismeretlen beavatkozás",'
                                          f'IF(COUNTIF(Cél!$A$17:$A${uh},E{r})=0,"ismeretlen veszély",IF(COUNTIF(Forgatókönyvek!$B$4:$B$60,A{r})=0,"nincs forgatókönyv",""))))')})
    legordulo(u, f"C4:C{uu}", TIPUSOK)
    f = wb.create_sheet("Forgatókönyvek")
    cimsor(f, "A veszteséghez vezető forgatókönyvek")
    uf = tablazat(f, 3, ["Forgatókönyv", "UCA", "Ok kategóriája", "Leírás", "Követelmény vagy intézkedés"], [13, 8, 34, 70, 50],
                  [list(x) for x in FORG], bemeneti_oszlopok=(1, 2, 3, 4, 5), uressor=57 - len(FORG))
    legordulo(f, f"C4:C{uf}", OKOK)
    o = wb.create_sheet("Összesítés")
    cimsor(o, "Lefedettség: UCA-k száma beavatkozásonként és típusonként")
    fejlec(o, 3, ["Beavatkozás"] + TIPUSOK + ["Összesen"], [16, 14, 14, 22, 22, 12])
    for i in range(15):
        r = 4 + i
        keplet(o.cell(row=r, column=1), f'=IF(Beavatkozások!A{4 + i}="","",Beavatkozások!A{4 + i})')
        for j, t in enumerate(TIPUSOK):
            keplet(o.cell(row=r, column=2 + j), f'=IF(A{r}="","",COUNTIFS(UCA!$B$4:$B${uu},A{r},UCA!$C$4:$C${uu},"{t}"))', "0")
        keplet(o.cell(row=r, column=6), f'=IF(A{r}="","",SUM(B{r}:E{r}))', "0", True)
    rr = 21
    fejlec(o, rr, ["Mutató", "Érték"], [44, 12])
    for k_, (t, fo) in enumerate([
            ("Veszélyek, amelyekhez nincs UCA", f'=SUMPRODUCT((Cél!A17:A{uh}<>"")*(COUNTIF(UCA!E4:E{uu},Cél!A17:A{uh})=0))'),
            ("UCA-k forgatókönyv nélkül", f'=COUNTIF(UCA!F4:F{uu},"nincs forgatókönyv")'),
            ("UCA-k száma", f'=COUNTA(UCA!A4:A{uu})'),
            ("Forgatókönyvek száma", f'=COUNTA(Forgatókönyvek!A4:A{uf})')]):
        szoveg(o.cell(row=rr + 1 + k_, column=1), t)
        keplet(o.cell(row=rr + 1 + k_, column=2), fo, "0", True)
    szoveg(o["A27"], "A „nem veszélyes” típusokat is érdemes rögzíteni (például egy megjegyzésben), hogy látszódjon: a kérdést megvizsgálták.")
    return mentes(wb, "stpa_sablon.xlsx")
