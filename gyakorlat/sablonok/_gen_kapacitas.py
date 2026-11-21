"""Kapacitás és szűk keresztmetszet (eszközlap: Kapacitás és szűk keresztmetszet)."""
from _kozos import *  # noqa: F401,F403

# erőforrás, típus, párhuzamos egységek, munkaigény [perc/egység]
ALAP = [("átvétel, diagnosztika", "dolgozó", 1, 6), ("mosás", "dolgozó", 1, 4), ("fékjavítás", "dolgozó", 2, 14),
        ("hajtáslánc-javítás", "dolgozó", 1, 9), ("végellenőrzés", "dolgozó", 1, 5)]
CSUCS = [("átvétel, diagnosztika", "dolgozó", 1, 6), ("mosás (+ lánctisztítás)", "dolgozó", 1, 7), ("fékjavítás", "dolgozó", 2, 14),
         ("hajtáslánc-javítás", "dolgozó", 1, 6), ("végellenőrzés", "dolgozó", 1, 5)]
N = 12
TERMEKEK = [("hagyományos", 30), ("elektromos", 10)]
TOBB = [("átvétel, diagnosztika", 1, 5, 9), ("mosás", 1, 4, 4), ("fékjavítás", 2, 13, 17),
        ("hajtáslánc-javítás", 1, 8, 12), ("végellenőrzés", 1, 4.5, 6.5)]


def egytermek_lap(wb, nev, cim, napi, muszak, ber, sorok):
    ws = wb.create_sheet(nev)
    cimsor(ws, cim)
    par = [("Kereslet [egység/nap]", napi, "0.0"), ("Napi munkaidő [óra]", muszak, "0.0"),
           ("Órabér a járulékokkal [Ft/óra] (példaérték)", ber, "#,##0")]
    for i, (t, v, fmt) in enumerate(par):
        szoveg(ws.cell(row=3 + i, column=1), t, felkov=True)
        bemenet(ws.cell(row=3 + i, column=2), v, fmt)
    szoveg(ws.cell(row=6, column=1), "Kereslet [egység/óra]", felkov=True)
    keplet(ws.cell(row=6, column=2), "=IF(B4=0,\"\",B3/B4)", "0.00", True)
    fej = ["Erőforrás", "Típus", "Párhuzamos egységek (m)", "Munkaigény p [perc/egység]", "Kapacitás [egység/óra]",
           "Szűk keresztmetszet", "Kihasználtság", "Kihasználatlan idő ciklusonként [perc]"]
    r1, rn = 9, 8 + N
    kepl = {5: lambda r: f'=IF(OR(A{r}="",N(D{r})=0),"",60*C{r}/D{r})',
            6: lambda r: f'=IF(E{r}="","",IF(E{r}=MIN($E${r1}:$E${rn}),"szűk keresztmetszet",""))',
            7: lambda r: f'=IF(E{r}="","",$B${rn + 5}/E{r})',
            8: lambda r: f'=IF(OR(E{r}="",B{r}<>"dolgozó"),"",C{r}*$B${rn + 7}-D{r})'}
    u = tablazat(ws, 8, fej, [30, 11, 13, 14, 13, 18, 13, 16], [list(s) for s in sorok],
                 bemeneti_oszlopok=(1, 2, 3, 4), kepletek=kepl, uressor=N - len(sorok),
                 formatumok={3: "0", 4: "0.00", 5: "0.00", 7: "0.0%", 8: "0.00"})
    legordulo(ws, f"B{r1}:B{u}", ["dolgozó", "gép"])
    r0 = u + 2
    rng = lambda c: f"${c}${r1}:${c}${u}"
    sor = [
        ("Folyamatkapacitás [egység/óra]", f"=MIN({rng('E')})", "0.00"),
        ("Szűk keresztmetszet", f"=INDEX({rng('A')},MATCH(B{r0},{rng('E')},0))", None),
        ("Korlát típusa", f'=IF($B$6>B{r0},"kapacitáskorlátos","keresletkorlátos")', None),
        ("Áram R = min(kereslet, kapacitás) [egység/óra]", f"=MIN($B$6,B{r0})", "0.00"),
        ("Napi kibocsátás [egység/nap]", f"=B{r0 + 3}*$B$4", "0.0"),
        ("Ciklusidő CT = 60 / R [perc]", f'=IF(B{r0 + 3}=0,"",60/B{r0 + 3})', "0.00"),
        ("Munkatartalom (dolgozók) [perc/egység]", f'=SUMIF({rng("B")},"dolgozó",{rng("D")})', "0.00"),
        ("Létszám (dolgozók)", f'=SUMIF({rng("B")},"dolgozó",{rng("C")})', "0"),
        ("Kihasználatlan idő ciklusonként összesen [perc]", f"=SUM({rng('H')})", "0.00"),
        ("Átlagos munkaerő-kihasználtság", f'=IF(OR(B{r0 + 5}="",B{r0 + 7}=0),"",B{r0 + 6}/(B{r0 + 5}*B{r0 + 7}))', "0.0%"),
        ("Közvetlen munkaerőköltség [Ft/egység]", f'=IF(B{r0 + 3}=0,"",B{r0 + 7}*$B$5/B{r0 + 3})', "#,##0"),
        ("Ebből a munkatartalom költsége [Ft/egység]", f"=B{r0 + 6}/60*$B$5", "#,##0"),
        ("A szűk keresztmetszet kihasználtsága", f"=B{r0 + 3}/B{r0}", "0.0%"),
    ]
    # a táblázat képletei a B{rn+5} (áram) és B{rn+7} (ciklusidő) cellára hivatkoznak: r0 = rn + 2
    assert r0 == rn + 2
    for k, (t, f, fmt) in enumerate(sor):
        szoveg(ws.cell(row=r0 + k, column=1), t)
        keplet(ws.cell(row=r0 + k, column=2), f, fmt, True)
    ws.column_dimensions["B"].width = 20
    ch = BarChart()
    ch.add_data(Reference(ws, min_col=7, min_row=8, max_row=8 + len(sorok)), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=9, max_row=8 + len(sorok)))
    diagram_kozos(ch, "Kihasználtság erőforrásonként", None, "kihasználtság", 18, 8)
    ch.y_axis.number_format = "0%"
    ch.legend = None
    ws.add_chart(ch, f"D{r0}")
    return ws, r0


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Kapacitás és szűk keresztmetszet – sablon", [
        "■ Mire való? Egy folyamat erőforrásainak kapacitása, a szűk keresztmetszet, a folyamat árama, az erőforrások és a munkaerő kihasználtsága, valamint a közvetlen munkaerőköltség egységenként (kézikönyv 19. fejezet; Cachon és Terwiesch, 2013, 3–4. fejezet).",
        "1. Az „Alap” lapon add meg a napi keresletet, a napi munkaidőt és az órabért.",
        "2. Soronként egy erőforrás a folyamat sorrendjében: megnevezés, típus (dolgozó vagy gép), a párhuzamosan dolgozó egységek száma (m) és az egy egységre jutó munkaigény percben (p).",
        "3. A kapacitás 60 · m / p egység/óra. A szűk keresztmetszet a legkisebb kapacitású erőforrás; a folyamat árama a kereslet és a kapacitás közül a kisebb; a kihasználtság az áram és a kapacitás hányadosa.",
        "4. A munkaerő-mutatók csak a „dolgozó” típusú sorokra vonatkoznak: munkatartalom, létszám, kihasználatlan idő, átlagos munkaerő-kihasználtság = munkatartalom / (ciklusidő · létszám), közvetlen munkaerőköltség = létszám · órabér / áram.",
        "5. A „Változat” lap ugyanez egy másik helyzetre (például csúcsidőszak, átcsoportosított feladatok); így két változat közvetlenül összevethető.",
        "6. A „Többtermékes” lap akkor kell, ha több terméktípus eltérő munkaigénnyel halad át ugyanazokon az erőforrásokon: a származtatott kihasználtság az összesített igény és a rendelkezésre álló idő hányadosa; a legnagyobb értékű erőforrás a szűk keresztmetszet.",
        "■ Példa: a VárosiBringa javítóműhelye (kézikönyv 19. fejezet). Az órabér példaérték.",
    ])
    egytermek_lap(wb, "Alap", "Alapállapot: napi 40 kerékpár", 40, 7.5, 4000, ALAP)
    egytermek_lap(wb, "Változat", "Változat: nyári csúcs (napi 55 kerékpár), a lánctisztítás a mosóhoz kerül", 55, 7.5, 4000, CSUCS)
    t = wb.create_sheet("Többtermékes")
    cimsor(t, "Több terméktípus: származtatott kihasználtság")
    szoveg(t["A3"], "Napi munkaidő [óra]", felkov=True)
    bemenet(t["B3"], 7.5, "0.0")
    szoveg(t["C5"], "Terméktípus →", felkov=True)
    szoveg(t["C6"], "Kereslet [egység/nap] →", felkov=True)
    for j in range(4):
        nev, d = TERMEKEK[j] if j < len(TERMEKEK) else (None, None)
        bemenet(t.cell(row=5, column=4 + j), nev)
        bemenet(t.cell(row=6, column=4 + j), d, "0")
    fej = ["Erőforrás", "Párhuzamos egységek (m)", "Rendelkezésre álló idő [perc/nap]", "1. termék p [perc]", "2. termék p [perc]",
           "3. termék p [perc]", "4. termék p [perc]", "Igény [perc/nap]", "Származtatott kihasználtság", "Szűk keresztmetszet"]
    r1, rn = 9, 8 + N
    kepl = {3: lambda r: f'=IF(A{r}="","",B{r}*$B$3*60)',
            8: lambda r: f'=IF(A{r}="","",SUMPRODUCT($D$6:$G$6,D{r}:G{r}))',
            9: lambda r: f'=IF(OR(A{r}="",N(C{r})=0),"",H{r}/C{r})',
            10: lambda r: f'=IF(I{r}="","",IF(I{r}=MAX($I${r1}:$I${rn}),"szűk keresztmetszet",""))'}
    sorok = [[a, m, None, p1, p2, None, None] for a, m, p1, p2 in TOBB]
    u = tablazat(t, 8, fej, [26, 12, 14, 12, 12, 12, 12, 12, 14, 18], sorok, bemeneti_oszlopok=(1, 2, 4, 5, 6, 7),
                 kepletek=kepl, uressor=N - len(TOBB), formatumok={2: "0", 3: "0", 4: "0.0", 5: "0.0", 6: "0.0", 7: "0.0", 8: "0", 9: "0.0%"})
    r0 = u + 2
    for k, (tx, f, fmt) in enumerate([
        ("Legnagyobb származtatott kihasználtság", f"=MAX(I{r1}:I{u})", "0.0%"),
        ("Szűk keresztmetszet", f"=INDEX(A{r1}:A{u},MATCH(B{r0},I{r1}:I{u},0))", None),
        ("Összes kereslet [egység/nap]", "=SUM(D6:G6)", "0"),
        ("Legnagyobb napi kibocsátás változatlan termékösszetétellel [egység/nap]", f'=IF(B{r0}=0,"",B{r0 + 2}/B{r0})', "0.0"),
    ]):
        szoveg(t.cell(row=r0 + k, column=1), tx)
        keplet(t.cell(row=r0 + k, column=2), f, fmt, True)
    szoveg(t.cell(row=r0 + 5, column=1), "Ha a származtatott kihasználtság 100% fölött van, a folyamat a jelenlegi termékösszetétellel nem tudja kiszolgálni a keresletet.")
    return mentes(wb, "kapacitas_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
