"""BPMN-modellezés (eszközlap: BPMN-modellezés): elemlista, modellellenőrzés, folyamatáram-elemzés."""
from _kozos import *  # noqa: F401,F403

TIPUSOK = ["indító esemény", "záró esemény", "köztes esemény", "feladat", "alfolyamat", "XOR", "ÉS", "VAGY", "külső résztvevő"]
FTIP = ["felhasználói", "automatikus", "kézi", "üzenetküldő", ""]
SAVOK = [("Vevő", "Vevő", 0), ("értékesítés", "ForgácsTech", 1), ("gyártáselőkészítés", "ForgácsTech", 2),
         ("gyártás", "ForgácsTech", 3), ("minőségügy, expediálás", "ForgácsTech", 4)]
# azonosító, típus, név, sáv, oszlop, idő [óra], feladattípus
ELEMEK = [
    ("VEVO", "külső résztvevő", "Vevő", "Vevő", None, None, ""),
    ("S", "indító esemény", "rendelés beérkezett", "értékesítés", 1, 0, ""),
    ("T1", "feladat", "rendelés rögzítése a MES-ben", "értékesítés", 2, 0.5, "felhasználói"),
    ("T2", "feladat", "kapacitás és anyag ellenőrzése", "gyártáselőkészítés", 2, 2, "felhasználói"),
    ("G1", "XOR", "tartható a határidő?", "gyártáselőkészítés", 3, 0, ""),
    ("T3", "feladat", "új határidő egyeztetése", "értékesítés", 3, 24, "felhasználói"),
    ("M1", "XOR", "", "értékesítés", 4, 0, ""),
    ("T4", "feladat", "visszaigazolás küldése", "értékesítés", 5, 0.5, "üzenetküldő"),
    ("A1", "ÉS", "", "gyártáselőkészítés", 5, 0, ""),
    ("T5", "feladat", "CAM-program, technológia", "gyártáselőkészítés", 6, 6, "felhasználói"),
    ("T6", "feladat", "anyag lefoglalása, előkészítése", "gyártás", 6, 4, "kézi"),
    ("A2", "ÉS", "", "gyártáselőkészítés", 7, 0, ""),
    ("T7", "feladat", "rendelés kiadása a gépre", "gyártáselőkészítés", 8, 22.5, "felhasználói"),
    ("T8", "feladat", "megmunkálás", "gyártás", 8, 2.5, "kézi"),
    ("T9", "feladat", "sorjázás, mosás", "gyártás", 9, 8.0, "kézi"),
    ("M2", "XOR", "", "minőségügy, expediálás", 10, 0, ""),
    ("T10", "feladat", "minőségellenőrzés", "minőségügy, expediálás", 11, 8.1, "kézi"),
    ("G2", "XOR", "megfelelő?", "minőségügy, expediálás", 12, 0, ""),
    ("T11", "feladat", "utómunka", "gyártás", 12, 2, "kézi"),
    ("T12", "feladat", "csomagolás, kiszállítás", "minőségügy, expediálás", 13, 7.9, "kézi"),
    ("E", "záró esemény", "rendelés teljesítve", "minőségügy, expediálás", 14, 0, ""),
]
# azonosító, honnan, hová, típus, címke, valószínűség
KAPCS = [
    ("F1", "S", "T1", "szekvencia", "", None), ("F2", "T1", "T2", "szekvencia", "", None), ("F3", "T2", "G1", "szekvencia", "", None),
    ("F4", "G1", "T3", "szekvencia", "nem", 0.2), ("F5", "G1", "M1", "szekvencia", "igen", 0.8), ("F6", "T3", "M1", "szekvencia", "", None),
    ("F7", "M1", "T4", "szekvencia", "", None), ("F8", "T4", "A1", "szekvencia", "", None), ("F9", "A1", "T5", "szekvencia", "", None),
    ("F10", "A1", "T6", "szekvencia", "", None), ("F11", "T5", "A2", "szekvencia", "", None), ("F12", "T6", "A2", "szekvencia", "", None),
    ("F13", "A2", "T7", "szekvencia", "", None), ("F14", "T7", "T8", "szekvencia", "", None), ("F15", "T8", "T9", "szekvencia", "", None),
    ("F16", "T9", "M2", "szekvencia", "", None), ("F17", "M2", "T10", "szekvencia", "", None), ("F18", "T10", "G2", "szekvencia", "", None),
    ("F19", "G2", "T11", "szekvencia", "nem", 0.05), ("F20", "G2", "T12", "szekvencia", "igen", 0.95), ("F21", "T11", "M2", "szekvencia", "", None),
    ("F22", "T12", "E", "szekvencia", "", None),
    ("U1", "VEVO", "S", "üzenet", "rendelés", None), ("U2", "T3", "VEVO", "üzenet", "határidő-javaslat", None),
    ("U3", "T4", "VEVO", "üzenet", "visszaigazolás", None), ("U4", "T12", "VEVO", "üzenet", "termék, szállítólevél", None),
]
NE, NK = 60, 90
# folyamatáram-blokkok: név, típus, ág1 idő, ág1 val. (ismétlésnél r), ág2 idő (ismétlésnél a javító lépés), ág2 val., ág3 idő, ág3 val.
BLOKK_JOVO = [
    ("rendelés rögzítése", "feladat", 0.5, None, None, None, None, None),
    ("kapacitás és anyag ellenőrzése (MES)", "feladat", 2, None, None, None, None, None),
    ("határidő: egyeztetés vagy nem", "XOR", 24, 0.2, 0, 0.8, None, None),
    ("visszaigazolás", "feladat", 0.5, None, None, None, None, None),
    ("CAM-program ∥ anyag", "ÉS", 6, None, 4, None, None, None),
    ("rendelés kiadása (várakozás a gépre)", "feladat", 22.5, None, None, None, None, None),
    ("megmunkálás", "feladat", 2.5, None, None, None, None, None),
    ("sorjázás, mosás", "feladat", 8.0, None, None, None, None, None),
    ("minőségellenőrzés utómunkával", "ismétlés", 8.1, 0.05, 2, None, None, None),
    ("csomagolás, kiszállítás", "feladat", 7.9, None, None, None, None, None),
]
BLOKK_JELEN = [
    ("rendelés rögzítése (papíron)", "feladat", 0.5, None, None, None, None, None),
    ("kapacitás becslése (termelésvezető)", "feladat", 16, None, None, None, None, None),
    ("határidő: egyeztetés vagy nem", "XOR", 24, 0.4, 0, 0.6, None, None),
    ("visszaigazolás", "feladat", 0.5, None, None, None, None, None),
]


def blokk_tabla(ws, kezdo, cim, sorok, ures, napi_cella):
    szoveg(ws.cell(row=kezdo - 1, column=1), cim, felkov=True)
    fej = ["Blokk", "Típus", "1. ág ideje [óra] / T", "1. ág valószínűsége / r", "2. ág ideje [óra] / javító lépés",
           "2. ág valószínűsége", "3. ág ideje [óra]", "3. ág valószínűsége", "A blokk ideje [óra]", "Ellenőrzés"]
    kepl = {9: lambda r: (f'=IF(A{r}="","",IF(B{r}="feladat",N(C{r}),IF(B{r}="XOR",N(C{r})*N(D{r})+N(E{r})*N(F{r})+N(G{r})*N(H{r}),'
                          f'IF(B{r}="ÉS",MAX(N(C{r}),N(E{r}),N(G{r})),IF(B{r}="ismétlés",IF(N(D{r})>=1,"",(N(C{r})+N(D{r})*N(E{r}))/(1-N(D{r}))),"")))))'),
            10: lambda r: (f'=IF(A{r}="","",IF(AND(B{r}="XOR",ABS(N(D{r})+N(F{r})+N(H{r})-1)>0.001),"a valószínűségek összege nem 1",'
                           f'IF(AND(B{r}="ismétlés",N(D{r})>=1),"r < 1 kell","rendben")))')}
    u = tablazat(ws, kezdo, fej, [38, 11, 13, 13, 15, 12, 12, 12, 13, 22], [list(s) for s in sorok],
                 bemeneti_oszlopok=(1, 2, 3, 4, 5, 6, 7, 8), kepletek=kepl, uressor=ures,
                 formatumok={3: "0.00", 4: "0.00", 5: "0.00", 6: "0.00", 7: "0.00", 8: "0.00", 9: "0.00"})
    legordulo(ws, f"B{kezdo + 1}:B{u}", ["feladat", "XOR", "ÉS", "ismétlés"])
    szoveg(ws.cell(row=u + 1, column=1), "Átlagos ciklusidő [óra]", felkov=True)
    keplet(ws.cell(row=u + 1, column=9), f"=SUM(I{kezdo + 1}:I{u})", "0.00", True)
    szoveg(ws.cell(row=u + 2, column=1), "Átlagos ciklusidő [munkanap]", felkov=True)
    keplet(ws.cell(row=u + 2, column=9), f'=IF(N({napi_cella})=0,"",I{u + 1}/{napi_cella})', "0.00", True)
    return u + 1


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "BPMN-modellezés – sablon", [
        "■ Mire való? Egy BPMN 2.0 folyamatmodell elemeinek és kapcsolatainak táblázatos rögzítése, szerkezeti ellenőrzése a modellezési irányelvek szerint, és a modell átlagos ciklusidejének kiszámítása folyamatáram-elemzéssel (kézikönyv 20. fejezet; OMG, 2011; Mendling és mtsai, 2010; Dumas és mtsai, 2018).",
        "1. A „Sávok” lapon sorold fel a résztvevőket (medencéket) és a sávokat felülről lefelé. Külső résztvevő (például a vevő) saját medence, belső működése nélkül.",
        "2. Az „Elemek” lapon soronként egy modellelem: azonosító, típus (indító, köztes vagy záró esemény, feladat, alfolyamat, XOR, ÉS, VAGY átjáró, külső résztvevő), név (feladatnál „ige + tárgy” szerkezetű), sáv, az elrendezéshez az oszlop sorszáma, átlagos idő órában (várakozással együtt), feladattípus.",
        "3. A „Kapcsolatok” lapon soronként egy folyam: honnan, hová, típus (szekvencia vagy üzenet), címke (feltétel), és a kizáró (XOR) átjárók kimenő ágainál a valószínűség.",
        "4. Az „Elemek” lap jobb oldala minden elemre megszámolja a bejövő és a kimenő szekvenciafolyamokat, és jelzi a szerkezeti problémákat; az „Ellenőrzés” lap a modell egészét értékeli a hét modellezési irányelv (7PMG) szerint.",
        "5. A „Folyamatáram” lapon a modellt soros blokkokra bontod: feladat; XOR (az ágak ideje és valószínűsége); ÉS (az ágak ideje, a leghosszabb számít); ismétlés (T: az ismételt lépés ideje, r: az ismétlés valószínűsége, javító lépés ideje; a blokk ideje (T + r · javító) / (1 − r)). Beágyazott blokknál az ág ideje egy másik blokk eredményére hivatkozhat.",
        "6. A bpmn notebook a két lapból BPMN 2.0 XML-fájlt készít (bpmn.io-ban megnyitható), szimulálja a ciklusidő eloszlását, és eseménynaplót generál a folyamatbányászati gyakorláshoz.",
        "■ Példa: a ForgácsTech rendelésteljesítési folyamatának jövőbeli modellje (kézikönyv 20. fejezet).",
    ])
    sv = wb.create_sheet("Sávok")
    cimsor(sv, "Résztvevők és sávok (felülről lefelé)")
    tablazat(sv, 3, ["Sáv", "Medence (résztvevő)", "Sorrend"], [30, 26, 10], [list(s) for s in SAVOK], bemeneti_oszlopok=(1, 2, 3), uressor=6)
    szoveg(sv["E3"], "Ha a medence egyetlen sávból áll, a sáv neve egyezzen a medence nevével.")

    el = wb.create_sheet("Elemek")
    cimsor(el, "A modell elemei")
    r1, rn = 4, 3 + NE
    k1, kn = 4, 3 + NK
    KH, KT, KTIP = f"Kapcsolatok!$B${k1}:$B${kn}", f"Kapcsolatok!$C${k1}:$C${kn}", f"Kapcsolatok!$D${k1}:$D${kn}"
    KVAL = f"Kapcsolatok!$F${k1}:$F${kn}"
    fej = ["Azonosító", "Típus", "Név", "Sáv", "Oszlop", "Idő [óra]", "Feladattípus", "Bejövő szekvencia", "Kimenő szekvencia",
           "XOR-ágak valószínűsége", "Ellenőrzés"]
    kepl = {8: lambda r: f'=IF(A{r}="","",COUNTIFS({KT},A{r},{KTIP},"szekvencia"))',
            9: lambda r: f'=IF(A{r}="","",COUNTIFS({KH},A{r},{KTIP},"szekvencia"))',
            10: lambda r: f'=IF(OR(A{r}="",B{r}<>"XOR"),"",IF(I{r}>1,SUMIFS({KVAL},{KH},A{r},{KTIP},"szekvencia"),""))',
            11: lambda r: (f'=IF(A{r}="","",IF(B{r}="külső résztvevő","",IF(H{r}+I{r}=0,"elszigetelt elem",'
                           f'IF(AND(B{r}="indító esemény",H{r}>0),"az indító eseménybe nem fut folyam",'
                           f'IF(AND(B{r}="záró esemény",I{r}>0),"a záró eseményből nem indul folyam",'
                           f'IF(AND(OR(B{r}="feladat",B{r}="alfolyamat"),OR(H{r}>1,I{r}>1)),"több be- vagy kimenet: használj átjárót",'
                           f'IF(AND(OR(B{r}="XOR",B{r}="ÉS",B{r}="VAGY"),H{r}>1,I{r}>1),"vegyes átjáró: bontsd kettőbe",'
                           f'IF(AND(J{r}<>"",ABS(N(J{r})-1)>0.001),"a valószínűségek összege nem 1",'
                           f'IF(AND(B{r}<>"záró esemény",I{r}=0),"nincs kimenet",IF(AND(B{r}<>"indító esemény",H{r}=0),"nincs bemenet","rendben"))))))))))')}
    u = tablazat(el, 3, fej, [11, 16, 34, 24, 8, 9, 13, 10, 10, 12, 34], [list(e) for e in ELEMEK],
                 bemeneti_oszlopok=(1, 2, 3, 4, 5, 6, 7), kepletek=kepl, uressor=NE - len(ELEMEK),
                 formatumok={6: "0.00", 10: "0.00"})
    legordulo(el, f"B{r1}:B{rn}", TIPUSOK)
    legordulo(el, f"G{r1}:G{rn}", FTIP[:-1])

    ka = wb.create_sheet("Kapcsolatok")
    cimsor(ka, "Szekvencia- és üzenetfolyamok")
    EA = f"Elemek!$A${r1}:$A${rn}"
    ED = f"Elemek!$D${r1}:$D${rn}"
    SA, SB = "Sávok!$A$4:$A$14", "Sávok!$B$4:$B$14"
    fej = ["Azonosító", "Honnan", "Hová", "Típus", "Címke (feltétel)", "Valószínűség", "Ellenőrzés"]
    kepl = {7: lambda r: (f'=IF(A{r}="","",IF(OR(COUNTIF({EA},B{r})=0,COUNTIF({EA},C{r})=0),"ismeretlen elem",'
                          f'IF(AND(D{r}="szekvencia",IFERROR(INDEX({SB},MATCH(INDEX({ED},MATCH(B{r},{EA},0)),{SA},0))<>'
                          f'INDEX({SB},MATCH(INDEX({ED},MATCH(C{r},{EA},0)),{SA},0)),FALSE)),"medencék között csak üzenetfolyam lehet",'
                          f'IF(AND(D{r}="üzenet",IFERROR(INDEX({SB},MATCH(INDEX({ED},MATCH(B{r},{EA},0)),{SA},0))='
                          f'INDEX({SB},MATCH(INDEX({ED},MATCH(C{r},{EA},0)),{SA},0)),FALSE)),"medencén belül szekvenciafolyam kell","rendben"))))')}
    tablazat(ka, 3, fej, [11, 11, 11, 12, 24, 12, 38], [list(k) for k in KAPCS], bemeneti_oszlopok=(1, 2, 3, 4, 5, 6),
             kepletek=kepl, uressor=NK - len(KAPCS), formatumok={6: "0.00"})
    legordulo(ka, f"D{k1}:D{kn}", ["szekvencia", "üzenet"])

    ell = wb.create_sheet("Ellenőrzés")
    cimsor(ell, "A modell ellenőrzése a hét modellezési irányelv (7PMG) szerint")
    ET = f"Elemek!$B${r1}:$B${rn}"
    EK = f"Elemek!$K${r1}:$K${rn}"
    sorok = [
        ("G1: a modell elemeinek száma (külső résztvevők nélkül)", f'=COUNTA({EA})-COUNTIF({ET},"külső résztvevő")',
         f'=IF(B4>50,"G7: 50 elem fölött bontsd alfolyamatokra","rendben")'),
        ("G2: a legtöbb be- vagy kimenő ág egy elemen", f"=MAX(Elemek!$H${r1}:$I${rn})", '=IF(B5>3,"sok ág egy elemen: egyszerűsíts","rendben")'),
        ("G3: indító események száma", f'=COUNTIF({ET},"indító esemény")', '=IF(B6=1,"rendben","egy indító esemény ajánlott")'),
        ("G3: záró események száma", f'=COUNTIF({ET},"záró esemény")', '=IF(B7=1,"rendben","egy záró esemény ajánlott")'),
        ("G4: elágazó és összefutó XOR átjárók különbsége", f'=COUNTIFS({ET},"XOR",Elemek!$I${r1}:$I${rn},">1")-COUNTIFS({ET},"XOR",Elemek!$H${r1}:$H${rn},">1")',
         '=IF(B8=0,"rendben","párosítatlan XOR átjáró")'),
        ("G4: elágazó és összefutó ÉS átjárók különbsége", f'=COUNTIFS({ET},"ÉS",Elemek!$I${r1}:$I${rn},">1")-COUNTIFS({ET},"ÉS",Elemek!$H${r1}:$H${rn},">1")',
         '=IF(B9=0,"rendben","párosítatlan ÉS átjáró")'),
        ("G5: VAGY átjárók száma", f'=COUNTIF({ET},"VAGY")', '=IF(B10=0,"rendben","kerüld a VAGY átjárót, ha lehet")'),
        ("Szerkezeti figyelmeztetések az Elemek lapon", f'=COUNTA({EA})-COUNTIF({ET},"külső résztvevő")-COUNTIF({EK},"rendben")',
         '=IF(B11=0,"rendben","nézd meg az Elemek lap Ellenőrzés oszlopát")'),
        ("Hibás kapcsolatok a Kapcsolatok lapon", f'=COUNTA(Kapcsolatok!$A${k1}:$A${kn})-COUNTIF(Kapcsolatok!$G${k1}:$G${kn},"rendben")',
         '=IF(B12=0,"rendben","nézd meg a Kapcsolatok lap Ellenőrzés oszlopát")'),
        ("Feladatok száma", f'=COUNTIF({ET},"feladat")+COUNTIF({ET},"alfolyamat")', '=IF(B13>=10,"rendben","a projektfeladatban legalább 10 tevékenység kell")'),
        ("Résztvevők (sávok) száma", "=COUNTA(Sávok!$A$4:$A$14)", '=IF(B14>=3,"rendben","a projektfeladatban legalább 3 résztvevő kell")'),
    ]
    fejlec(ell, 3, ["Szempont", "Érték", "Értékelés"], [56, 10, 52])
    for k, (t, f, e) in enumerate(sorok):
        r = 4 + k
        szoveg(ell.cell(row=r, column=1), t)
        keplet(ell.cell(row=r, column=2), f, "0", True)
        keplet(ell.cell(row=r, column=3), e)
    szoveg(ell["A16"], "G6 (ige + tárgy elnevezés) nem ellenőrizhető képlettel: nézd át a feladatneveket. A G2 itt a legnagyobb fokszámot mutatja; az irányelv a lehető legkevesebb ágat javasolja.")
    ell.merge_cells("A16:C17")
    ell.row_dimensions[16].height = 30

    fa = wb.create_sheet("Folyamatáram")
    cimsor(fa, "Folyamatáram-elemzés: az átlagos ciklusidő")
    szoveg(fa["A3"], "Napi munkaidő [óra]", felkov=True); bemenet(fa["B3"], 15, "0.0")
    v1 = blokk_tabla(fa, 6, "A) Jövőbeli folyamat: a rendeléstől a kiszállításig", BLOKK_JOVO, 6, "$B$3")
    s2 = v1 + 4
    v2 = blokk_tabla(fa, s2, "B) Jelenlegi folyamat: a rendeléstől a visszaigazolásig", BLOKK_JELEN, 4, "$B$3")
    r = v2 + 3
    szoveg(fa.cell(row=r, column=1), "A jövőbeli folyamat a visszaigazolásig (az A) táblázat első négy blokkja) [óra]", felkov=True)
    keplet(fa.cell(row=r, column=9), "=SUM(I7:I10)", "0.00", True)
    szoveg(fa.cell(row=r + 1, column=1), "Változás a visszaigazolásig", felkov=True)
    keplet(fa.cell(row=r + 1, column=9), f'=IF(N(I{v2})=0,"",I{r}/I{v2}-1)', "0%", True)
    return mentes(wb, "bpmn_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
