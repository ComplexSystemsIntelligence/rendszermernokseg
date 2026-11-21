"""FMEA-munkalap (eszközlap: FMEA)."""
from _kozos import *  # noqa: F401,F403
from openpyxl.formatting.rule import FormulaRule

SKALA = [  # pont, súlyosság, előfordulás, észlelhetőség
    (10, "veszélyes, figyelmeztetés nélkül: biztonságot vagy jogszabályi megfelelést érint", "legalább 100 hiba ezer egységre (állandóan jelen lévő)", "rejtett hiba, nincs ellenőrzés; szinte biztosan a vevőhöz jut"),
    (9, "veszélyes, figyelmeztetéssel", "kb. 50 ezer egységre", "nagyon kicsi esély a felfedezésre (ritka, kis mintás ellenőrzés)"),
    (8, "az alapvető funkció nem működik", "kb. 20 ezer egységre (gyakori)", "kicsi esély: felszínes szemrevételezés"),
    (7, "a funkció jelentősen romlik, a vevő nagyon elégedetlen", "kb. 10 ezer egységre", "kis mintás statisztikai ellenőrzés"),
    (6, "kényelmi funkció nem működik, a vevő elégedetlen", "kb. 5 ezer egységre (esetenkénti)", "közepes esély: manuális ellenőrzés minden darabon"),
    (5, "kényelmi funkció gyengén működik", "kb. 2 ezer egységre", "közepesen jó: nagy mintás statisztikai ellenőrzés"),
    (4, "illeszkedési, külalaki hiba, a vevők többsége észreveszi", "kb. 1 ezer egységre", "jó: mérőeszközös 100%-os ellenőrzés"),
    (3, "a vevők fele észreveszi", "kb. 0,5 ezer egységre (viszonylag kevés)", "nagyon jó: automatikus 100%-os ellenőrzés a folyamat után"),
    (2, "a vevők kisebb része észreveszi", "kb. 0,1 ezer egységre", "nagyon jó: automatikus ellenőrzés a hibát okozó lépésben"),
    (1, "nincs érzékelhető hatás", "legfeljebb 0,01 ezer egységre (nem valószínű)", "a hiba nem jöhet létre (hibabiztos kialakítás) vagy nyilvánvaló"),
]
FMEA = [  # az, elem, funkció, hibamód, hatás, S, ok, megelőző, O, észlelő, D, javasolt, felelős, határidő, végrehajtott, S', O', D'
    ("F1", "2.3 fedél ráhelyezése", "a fedél tömítő illesztése", "fordított fedél", "tömítetlen motor a vevőnél", 8, "szimmetrikus illesztés, gyenge visszajelzés", "–", 5,
     "szemrevételezés a végellenőrzésen", 7, "aszimmetrikus illesztőcsapok a befogóban", "gyártástervező", "FAT előtt", "beépítve", 8, 1, 1),
    ("F2", "3.2 hibás darab kiválogatása", "a hibás darab elkülönítése", "a darab a kiadóba kerül", "hibás motor a vevőnél", 8, "kihagyás: ritka, megszakító feladat", "HMI-jelzés", 3,
     "–", 8, "a kiadó csak a selejtdoboz érzékelőjének jelzése után enged", "automatizálási mérnök", "FAT előtt", "beépítve", 8, 3, 2),
    ("F3", "1.2 típusprogram ellenőrzése", "a helyes nyomatékprogram", "rossz program marad betöltve", "rossz nyomaték egy teljes sorozaton", 7, "a kezelő nem ellenőrzi a változatváltáskor", "eljárásleírás", 3,
     "első darab ellenőrzése", 5, "a HMI a gyártási rendelés alapján tölti be a programot", "szoftverfejlesztő", "SAT előtt", "beépítve", 7, 1, 5),
    ("F4", "csavaradagolás", "csavar biztosítása minden pozícióhoz", "hiányzó csavar", "laza fedél, tömítetlenség", 8, "az adagoló kiürül", "műszakindító ellenőrzés", 5,
     "csavarszámlálás a vezérlésben", 2, "töltöttségérzékelő az adagolóban", "gépész", "FAT előtt", "beépítve", 8, 3, 2),
    ("F5", "csavarmeghúzás", "nyomaték 4,0 ± 0,2 Nm", "alacsony nyomaték", "laza kötés a vevőnél", 8, "kopott bitbetét", "–", 4,
     "100%-os nyomatékmérés és -naplózás (R-09)", 2, "bitcsere a ciklusszám alapján", "karbantartás", "üzembe helyezés", "bevezetve", 8, 2, 2),
    ("F6", "2.2 motorház behelyezése", "teljes felfekvés a befogón", "nem ül fel teljesen", "a cella nem indul, időveszteség", 4, "megcsúszás a kezelő mozdulatában", "befogó vezetőélei", 6,
     "befogóérzékelő", 2, "", "", "", "", None, None, None),
    ("F7", "védőzóna figyelése", "a kezelő érzékelése a közös térben", "a lézerszkenner nem érzékeli a kezelőt", "ütközés teljes sebességgel, sérülés", 10, "szennyezett szkennerablak, elállított mező", "beüzemeléskori validálás", 2,
     "–", 6, "napi indítási teszt próbatesttel; az ablakszennyeződés önellenőrzése", "biztonsági felelős", "SAT előtt", "bevezetve", 10, 1, 2),
    ("F8", "fedél pozicionálása (kobot)", "a fedél pontos helyzete", "ferde fedél", "a csavar nem talál, a ciklus megszakad", 5, "a megfogó kopása", "karbantartási terv", 3,
     "a csavarozó hibajelzése", 2, "", "", "", "", None, None, None),
    ("F9", "adatátadás a MES-nek", "minden kötés adata a MES-ben (R-09)", "hiányzó nyomatékadatok", "reklamációnál nincs adat a kötésről", 6, "hálózati kiesés", "–", 3,
     "napi egyeztető riport", 4, "helyi adatpuffer a cellavezérlőben", "informatikus", "SAT előtt", "beépítve", 6, 1, 4),
]
N = 60


def prioritas(s, o, rpn):
    return (f'=IF(OR({s}="",{o}="",{rpn}=""),"",IF(AND({s}>=9,{o}>=2),"magas (súlyosság)",'
            f'IF({rpn}>Útmutató!$B$20,"magas",IF({rpn}>=Útmutató!$B$21,"közepes","alacsony"))))')


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "FMEA – hibamód- és hatáselemzés – sablon", [
        "■ Mire való? A rendszer elemeinek vagy a folyamat lépéseinek lehetséges hibamódjai, hatásaik és okaik, a kockázat értékelése és az intézkedések követése (kézikönyv 15. fejezet; AIAG–VDA hét lépése).",
        "1. A „Fejléc” lapon rögzítsd az FMEA azonosítóját, a vizsgált rendszert, a csapatot és a dátumokat.",
        "2. Az „FMEA” lapon soronként egy hibalánc: elem vagy folyamatlépés, funkció (mérhetően), hibamód (fizikai fogalommal), hibahatás (ahogy a vevő érzékeli), hibaok.",
        "3. Írd le a meglévő megelőző és észlelő intézkedéseket, majd értékeld a súlyosságot (S), az előfordulást (O) és az észlelhetőséget (D) a „Skálák” lap szerint. A skálákat a csapat előre egyeztesse; a 9–10-es súlyosság kritériumait ne módosítsd.",
        "4. A lap kiszámolja az RPN-t (S × O × D) és a prioritást egyszerűsített szabály szerint: ha S ≥ 9 és O ≥ 2, a prioritás mindig magas; egyébként az RPN küszöbei döntenek (lent állíthatók). Ez nem az AIAG–VDA cselekvési prioritás táblázata, hanem annak elvét követő egyszerűsítés.",
        "5. A magas és közepes prioritású sorokhoz írj intézkedést felelőssel és határidővel; a végrehajtás után add meg az új S, O, D értéket.",
        "6. A súlyosság csak konstrukciós változtatással csökken; ha nem változik, az új S oszlopba a régit írd.",
        "■ Példa: a KoboCella folyamat- és cella-FMEA-jának részlete (kézikönyv 15. fejezet).",
    ])
    ws0 = wb["Útmutató"]
    szoveg(ws0["A19"], "Prioritási küszöbök (RPN)", felkov=True)
    szoveg(ws0["A20"], "magas, ha RPN nagyobb, mint:"); bemenet(ws0["B20"], 100)
    szoveg(ws0["A21"], "közepes, ha RPN legalább:"); bemenet(ws0["B21"], 40)
    sk = wb.create_sheet("Skálák")
    cimsor(sk, "Súlyosság, előfordulás, észlelhetőség (1–10)", "A klasszikus autóipari skálák alapján, rövidítve. A csapat a projekthez igazíthatja, a 9–10-es súlyosságot kivéve.")
    tablazat(sk, 4, ["Pont", "Súlyosság (S): a hibahatás jelentősége", "Előfordulás (O): a hibaok gyakorisága", "Észlelhetőség (D): esély, hogy a hiba a vevőhöz jut"],
             [7, 60, 42, 60], SKALA, bemeneti_oszlopok=(2, 3, 4))
    fj = wb.create_sheet("Fejléc")
    cimsor(fj, "Az FMEA azonosító adatai")
    tablazat(fj, 3, ["Adat", "Érték"], [30, 70], [
        ["FMEA száma", "KC-PFMEA-01"], ["Rendszer, alrendszer vagy folyamat", "KoboCella: szerelési folyamat és cellafunkciók"],
        ["FMEA típusa", "folyamat-FMEA (cellafunkciókkal kiegészítve)"], ["Tervezésért felelős", "Kobold Hajtástechnika Kft., gyártástervezés"],
        ["Készítette", "a KoboCella projektcsapata"], ["Csapat", "gyártástervező, automatizálási mérnök, minőségügy, karbantartás, kezelő képviselője"],
        ["Kezdés dátuma", "a koncepció kiválasztása után"], ["Utolsó felülvizsgálat", "SAT előtt"]], bemeneti_oszlopok=(2,))
    ws = wb.create_sheet("FMEA")
    cimsor(ws, "FMEA-munkalap", "S: súlyosság, O: előfordulás, D: észlelhetőség (1–10). A ’ jel az intézkedés utáni értékelés.")
    fej = ["Az.", "Elem / folyamatlépés", "Funkció, követelmény", "Hibamód", "Hibahatás", "S", "Hibaok", "Megelőző intézkedés (meglévő)", "O",
           "Észlelő intézkedés (meglévő)", "D", "RPN", "Prioritás", "Javasolt intézkedés", "Felelős", "Határidő", "Végrehajtott intézkedés",
           "S’", "O’", "D’", "RPN’", "Prioritás’"]
    sor = [list(f[:12]) + [None, None] + list(f[12:15]) + list(f[15:18]) + [None, None] for f in FMEA]
    # sor felépítése: 0-10 az első 11 mező; 11: RPN (képlet) – igazítás
    sor = [[f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], f[10], None, None, f[11], f[12], f[13], f[14], f[15], f[16], f[17], None, None] for f in FMEA]
    kepl = {12: lambda r: f'=IF(OR(F{r}="",I{r}="",K{r}=""),"",F{r}*I{r}*K{r})', 13: lambda r: prioritas(f"F{r}", f"I{r}", f"L{r}"),
            21: lambda r: f'=IF(OR(R{r}="",S{r}="",T{r}=""),"",R{r}*S{r}*T{r})', 22: lambda r: prioritas(f"R{r}", f"S{r}", f"U{r}")}
    u = tablazat(ws, 4, fej, [6, 22, 24, 22, 24, 5, 26, 22, 5, 26, 5, 7, 16, 34, 16, 12, 14, 5, 5, 5, 7, 16], sor,
                 bemeneti_oszlopok=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20), kepletek=kepl, uressor=N - len(sor))
    for r in range(5, u + 1):
        for c in (6, 9, 11, 12, 18, 19, 20, 21):
            ws.cell(row=r, column=c).alignment = kozep
    for rng, e in ((f"M5:M{u}", "M5"), (f"V5:V{u}", "V5")):
        for szo, szin in (('LEFT({0},5)="magas"', "F6DEDE"), ('{0}="közepes"', "FBE7D9"), ('{0}="alacsony"', "DDEFE4")):
            ws.conditional_formatting.add(rng, FormulaRule(formula=[szo.format(e)], fill=PatternFill("solid", fgColor=szin)))
    for rg in (f"F5:F{u}", f"I5:I{u}", f"K5:K{u}", f"R5:T{u}"):
        legordulo(ws, rg, [str(i) for i in range(1, 11)])
    ws.freeze_panes = "E5"
    o = wb.create_sheet("Összesítés")
    cimsor(o, "Összesítés")
    fejlec(o, 3, ["Mutató", "Intézkedés előtt", "Intézkedés után"], [42, 16, 16])
    for k_, (t, f1, f2) in enumerate([
            ("Hibamódok száma", f"=COUNTA(FMEA!D5:D{u})", f"=COUNTA(FMEA!D5:D{u})"),
            ("Magas prioritás (súlyosság miatt is)", f'=COUNTIF(FMEA!M5:M{u},"magas*")', f'=COUNTIF(FMEA!V5:V{u},"magas*")+COUNTIFS(FMEA!V5:V{u},"",FMEA!M5:M{u},"magas*")'),
            ("Közepes prioritás", f'=COUNTIF(FMEA!M5:M{u},"közepes")', f'=COUNTIF(FMEA!V5:V{u},"közepes")+COUNTIFS(FMEA!V5:V{u},"",FMEA!M5:M{u},"közepes")'),
            ("Alacsony prioritás", f'=COUNTIF(FMEA!M5:M{u},"alacsony")', f'=COUNTIF(FMEA!V5:V{u},"alacsony")+COUNTIFS(FMEA!V5:V{u},"",FMEA!M5:M{u},"alacsony")'),
            ("9–10-es súlyosságú hibamódok", f'=COUNTIF(FMEA!F5:F{u},">=9")', f'=COUNTIF(FMEA!R5:R{u},">=9")+COUNTIFS(FMEA!R5:R{u},"",FMEA!F5:F{u},">=9")'),
            ("Legnagyobb RPN", f"=MAX(FMEA!L5:L{u})", f"=MAX(FMEA!U5:U{u})"),
            ("RPN-összeg (intézkedés nélküli soroknál a régi érték)", f"=SUM(FMEA!L5:L{u})", f'=SUM(FMEA!U5:U{u})+SUMIFS(FMEA!L5:L{u},FMEA!U5:U{u},"")')]):
        szoveg(o.cell(row=4 + k_, column=1), t)
        keplet(o.cell(row=4 + k_, column=2), f1, "0", True)
        keplet(o.cell(row=4 + k_, column=3), f2, "0", True)
    szoveg(o["A12"], "Megjegyzés: az RPN sorrendi skálákat szoroz; azonos RPN mögött eltérő kockázat állhat (kézikönyv 15.4. szakasz).")
    return mentes(wb, "fmea_sablon.xlsx")
