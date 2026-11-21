"""TRIZ: ellentmondások, 39 paraméter, 40 feltalálói elv (eszközlap: TRIZ)."""
from openpyxl.worksheet.datavalidation import DataValidation

from _kozos import *  # noqa: F401,F403

PARAM = ["A mozgó tárgy tömege", "Az álló tárgy tömege", "A mozgó tárgy hossza", "Az álló tárgy hossza",
         "A mozgó tárgy felülete", "Az álló tárgy felülete", "A mozgó tárgy térfogata", "Az álló tárgy térfogata",
         "Sebesség", "Erő", "Feszültség, nyomás", "Alak", "Az összetétel (szerkezet) stabilitása", "Szilárdság",
         "A mozgó tárgy működési ideje", "Az álló tárgy működési ideje", "Hőmérséklet", "Megvilágítás erőssége",
         "A mozgó tárgy energiafelhasználása", "Az álló tárgy energiafelhasználása", "Teljesítmény", "Energiaveszteség",
         "Anyagveszteség", "Információveszteség", "Időveszteség", "Anyagmennyiség", "Megbízhatóság", "Mérési pontosság",
         "Gyártási pontosság", "A tárgyat érő külső káros hatások", "A tárgy által keltett káros hatások", "Gyárthatóság",
         "Kezelhetőség (a használat egyszerűsége)", "Javíthatóság", "Alkalmazkodóképesség, sokoldalúság",
         "Az eszköz bonyolultsága", "Az észlelés és mérés nehézsége", "Az automatizáltság foka", "Termelékenység"]
PARAM_EN = ["Weight of moving object", "Weight of stationary object", "Length of moving object", "Length of stationary object",
            "Area of moving object", "Area of stationary object", "Volume of moving object", "Volume of stationary object",
            "Speed", "Force", "Stress or pressure", "Shape", "Stability of the object's composition", "Strength",
            "Duration of action of moving object", "Duration of action of stationary object", "Temperature",
            "Illumination intensity", "Use of energy by moving object", "Use of energy by stationary object", "Power",
            "Loss of energy", "Loss of substance", "Loss of information", "Loss of time", "Quantity of substance",
            "Reliability", "Measurement accuracy", "Manufacturing precision", "External harm affecting the object",
            "Object-generated harmful factors", "Ease of manufacture", "Ease of operation", "Ease of repair",
            "Adaptability or versatility", "Device complexity", "Difficulty of detecting and measuring",
            "Extent of automation", "Productivity"]
ELVEK = [
    ("Felosztás", "Segmentation", "A tárgy független részekre bontása, szétszedhetővé tétele, a felosztás fokának növelése.", "moduláris bútor, tagolt szállítószalag"),
    ("Eltávolítás", "Taking out", "A zavaró rész vagy tulajdonság leválasztása, illetve csak a szükséges rész kiemelése.", "a zajos kompresszor elhelyezése az épületen kívül"),
    ("Helyi minőség", "Local quality", "Homogén szerkezet helyett változó; minden rész a számára legkedvezőbb feltételek között működjön.", "edzett felületű, szívós magú fogaskerék"),
    ("Aszimmetria", "Asymmetry", "Szimmetrikus alak helyett aszimmetrikus; a meglévő aszimmetria fokozása.", "csak egy irányban bedugható csatlakozó"),
    ("Összevonás", "Merging", "Azonos vagy összetartozó tárgyak, műveletek egyesítése térben vagy időben.", "többorsós csavarozófej"),
    ("Egyetemesség", "Universality", "Egy rész több funkciót lásson el, így más részek feleslegessé válnak.", "kombinált fogó"),
    ("Beágyazás", "Nested doll", "Tárgyak egymásba helyezése, egyik a másik üregében.", "teleszkópos rúd, egymásba rakható dobozok"),
    ("Súlytalanság", "Anti-weight", "A tömeg ellensúlyozása más tárggyal vagy a környezet erőivel.", "rugós szerszámfelfüggesztés"),
    ("Ellentétes irányú megelőző beavatkozás", "Preliminary anti-action", "A később fellépő káros hatás előzetes ellensúlyozása.", "előfeszített beton"),
    ("Megelőző beavatkozás", "Preliminary action", "A szükséges változtatás (részben) előre elvégzése.", "előre töltött csavartár"),
    ("Megelőző hatáscsökkentés", "Beforehand cushioning", "Az alacsony megbízhatóság ellensúlyozása előre elhelyezett vészmegoldással.", "biztosíték, tartalék akkumulátor"),
    ("Azonos szintre hozás", "Equipotentiality", "Az emelés vagy süllyesztés szükségességének megszüntetése a munkakörülmények módosításával.", "állítható magasságú munkaasztal"),
    ("„Fordítva”", "The other way round", "A megszokott művelet megfordítása; a mozgó rész álljon, az álló mozogjon.", "forgóasztal a mozgó szerszám helyett"),
    ("Gömbölyítés és görbítés", "Spheroidality, curvature", "Egyenes vonalak és sík felületek helyett görbék; lineáris mozgás helyett forgó.", "görgősor"),
    ("Dinamika", "Dynamics", "A tárgy jellemzői változzanak, hogy minden munkafázisban optimálisak legyenek.", "állítható ülés, alakváltó megfogó"),
    ("Részleges vagy túlzott hatás", "Partial or excessive actions", "Ha a pontos hatás nehezen érhető el, alkalmazzunk valamivel kevesebbet vagy többet.", "túlfestés, majd a felesleg eltávolítása"),
    ("Más dimenzió", "Another dimension", "Mozgás vagy elrendezés két vagy három dimenzióban; többszintes elrendezés.", "emeletes kerékpártároló"),
    ("Mechanikus rezgés", "Mechanical vibration", "Rezgés alkalmazása vagy frekvenciájának növelése.", "rezgőadagoló"),
    ("Periodikus működés", "Periodic action", "Folytonos működés helyett szakaszos vagy impulzusos.", "impulzusos csavarozás"),
    ("A hasznos működés folytonossága", "Continuity of useful action", "A tárgy minden része folyamatosan, teljes terheléssel dolgozzon; üresjáratok megszüntetése.", "kétbefogós forgóasztal: egyik oldalon szerelnek, a másikon rakodnak"),
    ("Átsiklás", "Skipping", "A káros vagy veszélyes műveletet nagy sebességgel végezzük.", "gyors vágás a hőhatás csökkentésére"),
    ("A kár haszonná alakítása", "Blessing in disguise", "A káros hatás vagy tényező hasznos célra fordítása.", "hulladékhő hasznosítása"),
    ("Visszacsatolás", "Feedback", "Visszacsatolás bevezetése vagy módosítása.", "nyomatékszabályozott csavarozás"),
    ("Közvetítő", "Intermediary", "Közvetítő tárgy vagy folyamat alkalmazása.", "munkadarab-tartó paletta"),
    ("Önkiszolgálás", "Self-service", "A tárgy szolgálja ki önmagát, végezzen segéd- és javító műveleteket.", "öntisztító szűrő"),
    ("Másolás", "Copying", "Bonyolult, drága vagy veszélyes tárgy helyett egyszerűsített, olcsó másolat (kép, modell).", "digitális iker, szimulációs próbaüzem"),
    ("Olcsó, rövid élettartamú tárgyak", "Cheap short-living objects", "Drága, tartós tárgy helyett olcsó, cserélhető.", "eldobható bitbetét"),
    ("A mechanikus rendszer helyettesítése", "Mechanics substitution", "Mechanikus megoldás helyett optikai, akusztikus, elektromágneses mező.", "fényfüggöny a mechanikus védőrács helyett"),
    ("Pneumatika és hidraulika", "Pneumatics and hydraulics", "Szilárd részek helyett gáz vagy folyadék alkalmazása.", "pneumatikus befogó"),
    ("Hajlékony burkolatok és vékony filmek", "Flexible shells and thin films", "Merev szerkezetek helyett hajlékony burkolatok, vékony filmek.", "védőfólia"),
    ("Porózus anyagok", "Porous materials", "A tárgy porózussá tétele vagy porózus elemek alkalmazása.", "hangelnyelő burkolat"),
    ("Színváltoztatás", "Color changes", "A tárgy vagy környezete színének, átlátszóságának változtatása.", "színkódolt csavarok"),
    ("Homogenitás", "Homogeneity", "A kölcsönható tárgyak azonos (vagy hasonló tulajdonságú) anyagból készüljenek.", "azonos anyagú csavar és anya a korrózió ellen"),
    ("Elhagyás és visszanyerés", "Discarding and recovering", "A feladatát elvégzett rész tűnjön el vagy alakuljon át; a kopó rész álljon helyre.", "kioldódó támaszanyag a 3D nyomtatásban"),
    ("Paraméterváltoztatás", "Parameter changes", "A halmazállapot, koncentráció, rugalmasság, hőmérséklet változtatása.", "hőre lágyuló rögzítőelem"),
    ("Fázisátalakulás", "Phase transitions", "A fázisátalakulás közben fellépő jelenségek kihasználása.", "hőtároló anyag"),
    ("Hőtágulás", "Thermal expansion", "Az anyagok hőtágulásának kihasználása.", "zsugorkötés"),
    ("Erős oxidálószerek", "Strong oxidants", "A levegő helyett oxigéndús vagy más erős oxidáló közeg.", "oxigéndús égetés"),
    ("Inert környezet", "Inert atmosphere", "A szokásos környezet helyett semleges (inert) közeg.", "védőgázas hegesztés"),
    ("Kompozit anyagok", "Composite materials", "Homogén anyag helyett összetett (kompozit) anyag.", "szálerősítésű műanyag váz"),
]


def lista_dv(ws, tartomany, forras):
    dv = DataValidation(type="list", formula1=forras, allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(tartomany)


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "TRIZ – sablon", [
        "■ Mire való? Egy műszaki vagy fizikai ellentmondás megfogalmazása és feloldási irányok keresése a TRIZ eszközeivel (Altsuller).",
        "1. Az „Ellentmondás” lapon írd le a konkrét problémát, és fogalmazd meg műszaki ellentmondásként: melyik paraméter javítása melyik romlását okozza (a 39 paraméter listájából).",
        "2. Vizsgáld meg, megfogalmazható-e fizikai ellentmondásként: ugyanannak a jellemzőnek két ellentétes értéket kellene felvennie. Ha igen, válassz elválasztási elvet (idő, tér, feltétel, rendszerszint).",
        "3. Válassz legfeljebb öt feltalálói elvet a „40 elv” lapról (a listából), és mindegyikhez írj legalább egy konkrét ötletet. Az ellentmondásmátrix a szakirodalomban és a TRIZ-szoftverekben elérhető; ez a sablon nem tartalmazza.",
        "4. Fogalmazd meg az ideális végeredményt: a funkció teljesül, de nincs költsége, káros hatása és helyigénye. Ez segít elszakadni a meglévő megoldásoktól.",
        "5. Az ötleteket értékeld (megvalósíthatóság, hatás), és a legjobbakat vidd tovább a koncepció-kiválasztásba.",
        "■ Példa: a VárosiBringa zárjának ellentmondása (kézikönyv 9. fejezet).",
    ])
    pl = wb.create_sheet("39 paraméter")
    cimsor(pl, "A 39 általános műszaki paraméter", "Altsuller listája (magyar és angol megnevezés).")
    tablazat(pl, 4, ["Sorszám", "Paraméter", "Angol megnevezés"], [9, 42, 40],
             [[i + 1, p, e] for i, (p, e) in enumerate(zip(PARAM, PARAM_EN))])
    el = wb.create_sheet("40 elv")
    cimsor(el, "A 40 feltalálói elv", "Rövid leírás és általános példa elvenként.")
    tablazat(el, 4, ["Sorszám", "Elv", "Angol megnevezés", "Leírás", "Általános példa"], [9, 34, 28, 60, 40],
             [[i + 1, a, b, c, d] for i, (a, b, c, d) in enumerate(ELVEK)])
    for r in range(5, 45):
        el.row_dimensions[r].height = 28
    ws = wb.create_sheet("Ellentmondás")
    cimsor(ws, "Ellentmondás-munkalap")
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 44
    ws.column_dimensions["C"].width = 54
    adat = [
        ("Konkrét probléma", "A kerékpárzárnak gyorsan nyithatónak kell lennie (kölcsönzéskor), de nehezen feltörhetőnek (lopás ellen)."),
        ("Ideális végeredmény", "A kerékpár magától a helyén marad, amíg a jogosult felhasználó el nem viszi."),
    ]
    r = 4
    for t, v in adat:
        szoveg(ws.cell(row=r, column=1), t, felkov=True)
        bemenet(ws.cell(row=r, column=2), v)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
        ws.row_dimensions[r].height = 36
        r += 1
    r += 1
    fejlec(ws, r, ["Műszaki ellentmondás", "Paraméter (a listából)", "Leírás a saját szavaiddal"])
    for t, p, d in [("Javítandó paraméter", "Kezelhetőség (a használat egyszerűsége)", "gyors, egyszerű nyitás"),
                    ("Romló paraméter", "Szilárdság", "a zár mechanikai ellenállása feltöréssel szemben")]:
        r += 1
        szoveg(ws.cell(row=r, column=1), t, felkov=True)
        bemenet(ws.cell(row=r, column=2), p)
        bemenet(ws.cell(row=r, column=3), d)
        lista_dv(ws, f"B{r}", "='39 paraméter'!$B$5:$B$43")
    r += 2
    fejlec(ws, r, ["Fizikai ellentmondás", "Megfogalmazás", "Elválasztási elv"])
    r += 1
    szoveg(ws.cell(row=r, column=1), "Ugyanannak a jellemzőnek …", felkov=True)
    bemenet(ws.cell(row=r, column=2), "A reteszelőelemnek merevnek kell lennie (feltörés ellen) és könnyen mozdulónak (gyors nyitáshoz).")
    bemenet(ws.cell(row=r, column=3), "feltétel szerint")
    legordulo(ws, f"C{r}", ["időben", "térben", "feltétel szerint", "rendszerszintek között"])
    ws.row_dimensions[r].height = 36
    r += 2
    fejlec(ws, r, ["Választott feltalálói elv (a listából)", "Az elv leírása (automatikus)", "Konkrét ötlet a problémára"])
    otletek = [("Dinamika", "Mechanikusan önzáró retesz, amelyet csak hitelesített jelre működő kis aktuátor old ki."),
               ("Megelőző beavatkozás", "A kioldást a kölcsönzés jóváhagyásakor előkészítjük, a felhasználó odaérése előtt."),
               ("A mechanikus rendszer helyettesítése", "A fizikai ellenállás egy részét helymeghatározás és riasztás váltja ki."),
               (None, None), (None, None)]
    elso = r + 1
    for e, o in otletek:
        r += 1
        bemenet(ws.cell(row=r, column=1), e)
        keplet(ws.cell(row=r, column=2), f"=IF(A{r}=\"\",\"\",IFERROR(INDEX('40 elv'!$D$5:$D$44,MATCH(A{r},'40 elv'!$B$5:$B$44,0)),\"nincs ilyen elv a listában\"))")
        bemenet(ws.cell(row=r, column=3), o)
        ws.row_dimensions[r].height = 40
    lista_dv(ws, f"A{elso}:A{r}", "='40 elv'!$B$5:$B$44")
    r += 2
    fejlec(ws, r, ["Ötlet értékelése", "Megvalósíthatóság (1–5)", "Várható hatás (1–5)"])
    for i in range(3):
        r += 1
        keplet(ws.cell(row=r, column=1), f'=IF(C{elso + i}="","",C{elso + i})')
        bemenet(ws.cell(row=r, column=2), [4, 5, 3][i])
        bemenet(ws.cell(row=r, column=3), [5, 3, 3][i])
    return mentes(wb, "triz_sablon.xlsx")
