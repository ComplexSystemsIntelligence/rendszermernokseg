"""Folyamatábra és értékáram-térkép (eszközlap: Folyamatábra és értékáram-térkép)."""
from _kozos import *  # noqa: F401,F403

SZIMB = ["művelet", "ellenőrzés", "szállítás", "tárolás", "várakozás"]
ERTEK = ["értékteremtő", "szükséges", "veszteség"]

# lépés, szimbólum, erőforrás, műveleti idő [h], ebből beállítás [h], várakozás előtte [nap], várakozó egységek, érték, megjegyzés
JELENLEGI = [
    ("gyártáselőkészítés (CAM, technológia)", "művelet", "technológus", 0.8, 0.0, 1.5, 9, "szükséges", "a rendelések sorban állnak a technológusnál"),
    ("anyag-előkészítés (fűrészelés)", "művelet", "szalagfűrész", 0.3, 0.05, 2.5, 15, "értékteremtő", "anyagra várás: a beszerzés a kiadás után indul"),
    ("megmunkálás", "művelet", "többtengelyes megmunkáló központ", 3.2, 0.8, 3.0, 18, "értékteremtő", "gépre várás; átállás 48 perc"),
    ("sorjázás, mosás", "művelet", "kézi munkahely", 0.5, 0.0, 1.0, 6, "értékteremtő", ""),
    ("minőségellenőrzés", "ellenőrzés", "3D mérőgép", 0.6, 0.0, 1.0, 6, "szükséges", "a mérőgép előtt kötegelve várnak"),
    ("csomagolás, kiszállítás", "szállítás", "expediálás", 0.4, 0.0, 1.0, 6, "szükséges", "heti két kiszállítási nap"),
]
JOVOBELI = [
    ("gyártáselőkészítés (CAM, technológia)", "művelet", "technológus", 0.8, 0.0, 0.5, 3, "szükséges", "a rendeléskiadás a megmunkáló központ kapacitásához kötve"),
    ("anyag-előkészítés (fűrészelés)", "művelet", "szalagfűrész", 0.3, 0.05, 0.5, 3, "értékteremtő", "anyaglefoglalás a rendelés kiadásakor"),
    ("megmunkálás", "művelet", "többtengelyes megmunkáló központ", 2.53, 0.13, 1.5, 9, "értékteremtő", "SMED: átállás 8 perc, fele akkora sorozatok"),
    ("sorjázás, mosás", "művelet", "kézi munkahely", 0.5, 0.0, 0.5, 3, "értékteremtő", ""),
    ("minőségellenőrzés", "ellenőrzés", "3D mérőgép", 0.6, 0.0, 0.5, 3, "szükséges", "darabonkénti mérés kötegelés nélkül"),
    ("csomagolás, kiszállítás", "szállítás", "expediálás", 0.4, 0.0, 0.5, 3, "szükséges", "napi kiszállítás"),
]
N = 15
VESZTESEGEK = [
    ("túltermelés", "a szükségesnél több vagy korábban gyártunk", "a sürgős rendelés miatt a teljes nyersdarab-köteget legyártják", "megmunkálás", "a sorozatnagyság a rendeléshez igazodjon"),
    ("várakozás", "ember, gép vagy munkadarab vár", "a rendelés átlagosan 3 napot vár a megmunkáló központ előtt", "megmunkálás", "rendeléskiadás a szűk keresztmetszet kapacitásához"),
    ("szállítás", "felesleges anyagmozgatás", "a darabok kétszer járják meg a raktárat a mosás előtt", "sorjázás, mosás", "a mosó a megmunkáló központ mellé kerül"),
    ("felesleges feldolgozás", "a vevő által nem kért pontosság vagy művelet", "minden méretet 3D mérőgépen mérnek, a nem kritikusakat is", "minőségellenőrzés", "mérési terv a kritikus méretekre"),
    ("készlet", "a szükségesnél több anyag, félkész vagy kész termék", "60 rendelés van egyszerre folyamatban", "teljes folyamat", "a folyamatban lévő rendelések számának korlátozása"),
    ("felesleges mozgás", "keresés, nyúlás, gyaloglás", "az átállásnál a szerszámokat és készülékeket keresik", "megmunkálás", "SMED: előkészítés a gép futása alatt"),
    ("hibás termék", "selejt, utómunka, ismételt ellenőrzés", "az első darab gyakran utánállítást igényel", "megmunkálás", "szerszám-előbeállítás"),
]


def ertekaram_lap(wb, nev, cim, adatok, napi_ora, keszlet, aram):
    ws = wb.create_sheet(nev)
    cimsor(ws, cim)
    for i, (t, v, fmt) in enumerate([("Napi munkaidő [óra]", napi_ora, "0.0"),
                                      ("Folyamatban lévő egységek száma (készlet, I)", keszlet, "0"),
                                      ("Kibocsátás [egység/nap] (áram, R)", aram, "0.0")]):
        szoveg(ws.cell(row=3 + i, column=1), t, felkov=True)
        bemenet(ws.cell(row=3 + i, column=2), v, fmt)
    fej = ["Lépés", "Szimbólum", "Erőforrás", "Műveleti idő [óra/egység]", "Ebből beállítás [óra]",
           "Várakozás a lépés előtt [nap]", "Várakozó egységek a lépés előtt", "Érték a vevőnek", "Megjegyzés",
           "Várakozás [óra]", "Kumulált átfutás [óra]"]
    kepl = {10: lambda r: f'=IF(A{r}="","",F{r}*$B$3)',
            11: lambda r: f'=IF(A{r}="","",SUM($J$8:J{r})+SUM($D$8:D{r}))'}
    u = tablazat(ws, 7, fej, [36, 12, 28, 13, 12, 13, 13, 14, 40, 12, 13], [list(a) for a in adatok],
                 bemeneti_oszlopok=(1, 2, 3, 4, 5, 6, 7, 8, 9), kepletek=kepl, uressor=N - len(adatok),
                 formatumok={4: "0.00", 5: "0.00", 6: "0.0", 7: "0", 10: "0.0", 11: "0.0"})
    legordulo(ws, f"B8:B{u}", SZIMB)
    legordulo(ws, f"H8:H{u}", ERTEK)
    r0 = u + 3
    szoveg(ws.cell(row=r0 - 1, column=1), "Összesítés", felkov=True)
    sorok = [
        ("Műveleti idő összesen [óra]", f"=SUM(D8:D{u})", "0.00"),
        ("Ebből értékteremtő lépések ideje [óra]", f'=SUMIF(H8:H{u},"értékteremtő",D8:D{u})', "0.00"),
        ("Ebből beállítás [óra]", f"=SUM(E8:E{u})", "0.00"),
        ("Átfutási idő a térkép szerint [nap] (a várakozások összege)", f"=SUM(F8:F{u})", "0.0"),
        ("Átfutási idő [óra]", f"=B{r0 + 3}*$B$3", "0.0"),
        ("Folyamathatékonyság (műveleti idő / átfutás)", f'=IF(B{r0 + 4}=0,"",B{r0}/B{r0 + 4})', "0.0%"),
        ("Értékteremtő arány (értékteremtő idő / átfutás)", f'=IF(B{r0 + 4}=0,"",B{r0 + 1}/B{r0 + 4})', "0.0%"),
        ("Várakozó egységek a térkép szerint", f"=SUM(G8:G{u})", "0"),
        ("Átfutás a Little-törvény szerint [nap] (I / R)", '=IF($B$5=0,"",$B$4/$B$5)', "0.0"),
        ("Eltérés a térkép és a Little-törvény között", f'=IF(OR(B{r0 + 8}="",B{r0 + 3}=0),"",B{r0 + 8}/B{r0 + 3}-1)', "0%"),
        ("Leghosszabb várakozás [nap]", f"=MAX(F8:F{u})", "0.0"),
        ("A leghosszabb várakozás helye", f'=IF(B{r0 + 10}=0,"",INDEX(A8:A{u},MATCH(B{r0 + 10},F8:F{u},0)))', None),
    ]
    for k, (t, f, fmt) in enumerate(sorok):
        szoveg(ws.cell(row=r0 + k, column=1), t)
        keplet(ws.cell(row=r0 + k, column=2), f, fmt, True)
    ws.column_dimensions["B"].width = 18
    ch = BarChart()
    ch.type = "bar"
    ch.grouping = "clustered"
    ch.add_data(Reference(ws, min_col=10, min_row=7, max_row=7 + len(adatok)), titles_from_data=True)
    ch.add_data(Reference(ws, min_col=4, min_row=7, max_row=7 + len(adatok)), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=8, max_row=7 + len(adatok)))
    ch.y_axis.scaling.orientation = "minMax"
    ch.x_axis.scaling.orientation = "maxMin"
    diagram_kozos(ch, "Várakozás és műveleti idő lépésenként [óra]", None, "óra", 22, 9)
    ws.add_chart(ch, f"D{r0}")
    return ws, r0


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Folyamatábra és értékáram-térkép – sablon", [
        "■ Mire való? Egy termék vagy rendelés útjának feltérképezése a folyamaton át: a lépések, a lépések közötti várakozás és készlet, a műveleti és az átfutási idő, a folyamathatékonyság és a veszteségek (kézikönyv 19. fejezet; Rother és Shook, 1999).",
        "1. A „Jelenlegi” lapon add meg a napi munkaidőt, a folyamatban lévő egységek számát és a napi kibocsátást (ezekkel a Little-törvény ellenőrzi a térképet).",
        "2. Soronként egy folyamatlépés a folyamat sorrendjében: megnevezés, szimbólum (művelet, ellenőrzés, szállítás, tárolás, várakozás), erőforrás, egységnyi műveleti idő órában (ebből a beállítás), a lépés előtti átlagos várakozás napban, a lépés előtt várakozó egységek száma, és hogy a lépés a vevő szemében értékteremtő, szükséges (de nem értékteremtő) vagy veszteség.",
        "3. Az adatokat a helyszínen, a folyamatot végigjárva gyűjtsd: a várakozó egységeket számold meg, a műveleti időket mérd. A várakozási idő a várakozó egységek és a napi kibocsátás hányadosaként is becsülhető.",
        "4. Az összesítés: műveleti idő, átfutási idő (Rother és Shook szerint a várakozások összege), folyamathatékonyság, értékteremtő arány, a Little-törvény ellenőrzése és a leghosszabb várakozás helye. Ha a térkép és a Little-törvény nagyon eltér, valamelyik adat hibás vagy a rendszerhatár nem egyezik.",
        "5. A „Veszteségek” lapon gyűjtsd össze Ohno hét veszteségének megfigyelt példáit és a fejlesztési ötleteket.",
        "6. A „Jövőbeli” lapon tervezd meg a célállapotot, az „Összevetés” lap a két állapotot hasonlítja össze.",
        "■ Példa: a ForgácsTech egy rendelésének értékárama (kézikönyv 19. fejezet).",
    ])
    _, j0 = ertekaram_lap(wb, "Jelenlegi", "Jelenlegi állapot", JELENLEGI, 15, 60, 6)
    v = wb.create_sheet("Veszteségek")
    cimsor(v, "Ohno hét vesztesége: megfigyelések és ötletek")
    u = tablazat(v, 3, ["Veszteség", "Mit jelent?", "Megfigyelt példa", "Folyamatlépés", "Fejlesztési ötlet", "Prioritás"],
                 [20, 34, 44, 20, 40, 11], [list(x) + ["magas" if i in (1, 4, 5) else "közepes"] for i, x in enumerate(VESZTESEGEK)],
                 bemeneti_oszlopok=(3, 4, 5, 6), uressor=5)
    legordulo(v, f"F4:F{u}", ["magas", "közepes", "alacsony"])
    _, f0 = ertekaram_lap(wb, "Jövőbeli", "Jövőbeli állapot", JOVOBELI, 15, 24, 6)
    o = wb.create_sheet("Összevetés")
    cimsor(o, "A jelenlegi és a jövőbeli állapot összevetése")
    fejlec(o, 3, ["Mutató", "Jelenlegi", "Jövőbeli", "Változás"], [52, 14, 14, 14])
    mut = [("Műveleti idő összesen [óra]", 0, "0.00"), ("Átfutási idő [nap]", 3, "0.0"),
           ("Folyamathatékonyság", 5, "0.0%"), ("Értékteremtő arány", 6, "0.0%"),
           ("Várakozó egységek", 7, "0"), ("Leghosszabb várakozás [nap]", 10, "0.0")]
    for k, (t, d, fmt) in enumerate(mut):
        r = 4 + k
        szoveg(o.cell(row=r, column=1), t)
        keplet(o.cell(row=r, column=2), f"=Jelenlegi!B{j0 + d}", fmt)
        keplet(o.cell(row=r, column=3), f"=Jövőbeli!B{f0 + d}", fmt)
        keplet(o.cell(row=r, column=4), f'=IF(N(B{r})=0,"",C{r}/B{r}-1)', "0%", True)
    szoveg(o["A11"], "A változás a jövőbeli érték relatív eltérése a jelenlegitől (például −60% = 60%-kal kisebb).")
    return mentes(wb, "folyamatabra_vsm_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
