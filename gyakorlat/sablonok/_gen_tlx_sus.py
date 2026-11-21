"""NASA-TLX és SUS kiértékelés (eszközlap: NASA-TLX és SUS)."""
from _kozos import *  # noqa: F401,F403

MAN = [[30, 60, 65, 50, 50, 20], [35, 55, 50, 40, 80, 30], [45, 55, 50, 25, 65, 35], [40, 50, 60, 20, 40, 25],
       [20, 50, 40, 35, 70, 25], [40, 65, 65, 25, 60, 50], [50, 40, 45, 45, 50, 35], [35, 65, 65, 35, 85, 35]]
COB = [[40, 30, 30, 25, 40, 30], [45, 15, 30, 5, 50, 20], [60, 40, 45, 20, 50, 10], [30, 10, 35, 15, 30, 30],
       [45, 35, 25, 15, 45, 20], [25, 25, 50, 15, 60, 35], [30, 25, 55, 30, 35, 20], [40, 15, 30, 15, 55, 25]]
W = [[3, 4, 3, 2, 3, 0], [3, 4, 4, 1, 3, 0], [3, 3, 4, 2, 2, 1], [2, 5, 4, 1, 3, 0], [2, 3, 5, 0, 4, 1],
     [4, 4, 4, 0, 2, 1], [1, 4, 4, 2, 4, 0], [4, 3, 5, 1, 2, 0]]
SUS1 = [[4, 4, 5, 2, 3, 2, 3, 3, 4, 3], [5, 2, 4, 2, 4, 2, 3, 2, 4, 3], [3, 3, 4, 2, 3, 2, 1, 4, 4, 3], [4, 4, 3, 5, 5, 3, 4, 2, 4, 2],
        [5, 1, 5, 2, 3, 2, 3, 1, 4, 2], [3, 3, 3, 3, 3, 4, 3, 3, 3, 3], [3, 5, 3, 3, 4, 3, 3, 3, 2, 3], [4, 2, 4, 1, 4, 2, 2, 2, 4, 1],
        [2, 2, 3, 3, 3, 3, 2, 1, 3, 1], [4, 2, 3, 2, 4, 2, 4, 3, 4, 2], [3, 3, 3, 3, 3, 3, 3, 2, 4, 3], [5, 2, 5, 2, 5, 2, 4, 1, 5, 1]]
SUS2 = [[4, 2, 3, 1, 4, 2, 4, 1, 4, 2], [4, 2, 4, 2, 3, 2, 5, 3, 4, 1], [4, 2, 4, 2, 4, 2, 4, 2, 3, 1], [5, 1, 4, 3, 4, 2, 4, 1, 5, 1],
        [4, 2, 5, 1, 3, 2, 4, 1, 3, 2], [4, 2, 4, 4, 3, 2, 4, 1, 5, 2], [2, 2, 4, 3, 5, 1, 4, 3, 4, 3], [5, 1, 5, 3, 5, 2, 5, 2, 4, 2],
        [3, 1, 3, 1, 4, 1, 5, 3, 5, 1], [4, 2, 4, 1, 3, 2, 5, 1, 4, 1], [4, 3, 4, 2, 4, 3, 4, 1, 4, 2], [5, 1, 4, 1, 5, 1, 5, 1, 5, 2]]
SIKER1 = [[1, 1, 0, 1], [1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 0, 1], [1, 1, 1, 1], [1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 1, 1],
          [1, 1, 0, 0], [1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]
SIKER2 = [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 0, 1], [1, 1, 1, 1],
          [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 0], [1, 1, 1, 1]]
ALSKALAK = ["Szellemi igénybevétel", "Fizikai igénybevétel", "Időbeli nyomás", "Teljesítmény (0 = tökéletes)", "Erőfeszítés", "Frusztráció"]
SUS_KERDES = [
    "Szívesen használnám gyakran ezt a rendszert.", "A rendszert feleslegesen bonyolultnak találtam.",
    "Könnyen használhatónak találtam a rendszert.", "Szükségem lenne egy hozzáértő segítségére a használatához.",
    "A rendszer funkciói jól illeszkednek egymáshoz.", "Túl sok ellentmondást találtam a rendszerben.",
    "Úgy gondolom, a legtöbben gyorsan megtanulnák a használatát.", "Nagyon nehézkesnek találtam a használatát.",
    "Magabiztosnak éreztem magam a használata közben.", "Sok mindent meg kellett tanulnom, mielőtt használni tudtam."]
NP = 20


def tlx_blokk(ws, r0, cim, adat):
    szoveg(ws.cell(row=r0, column=1), cim, felkov=True)
    fej = ["Résztvevő"] + ALSKALAK + ["Nyers TLX", "Súlyozott TLX"]
    kepl = {8: lambda r: f'=IF(COUNT(B{r}:G{r})<6,"",AVERAGE(B{r}:G{r}))',
            9: lambda r: f'=IF(OR(COUNT(B{r}:G{r})<6,Súlyok!H{r - r0 + 2}<>15),"",SUMPRODUCT(B{r}:G{r},Súlyok!B{r - r0 + 2}:G{r - r0 + 2})/15)'}
    u = tablazat(ws, r0 + 1, fej, [12] + [14] * 6 + [11, 13], [[f"R{i + 1}"] + a for i, a in enumerate(adat)],
                 bemeneti_oszlopok=range(1, 8), kepletek=kepl, uressor=NP - len(adat), formatumok={8: "0.0", 9: "0.0"})
    szoveg(ws.cell(row=u + 1, column=1), "Átlag", felkov=True)
    for c in range(2, 10):
        col = get_column_letter(c)
        keplet(ws.cell(row=u + 1, column=c), f'=IF(COUNT({col}{r0 + 2}:{col}{u})=0,"",AVERAGE({col}{r0 + 2}:{col}{u}))', "0.0", True)
    return u + 1


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "NASA-TLX és SUS – sablon", [
        "■ Mire való? A szubjektív munkaterhelés (NASA-TLX, Hart–Staveland) és az észlelt használhatóság (SUS, Brooke) mérése és két változat összevetése.",
        "NASA-TLX: hat alskála 0–100 között, 5-ös lépésekben (a teljesítménynél 0 = tökéletes, 100 = sikertelen). A nyers TLX a hat érték átlaga. A súlyozott TLX-hez a résztvevő 15 páros összehasonlításban dönti el, melyik alskála járult hozzá jobban a terheléséhez; a „Súlyok” lapon az alskálánként kapott győzelmek száma (0–5, összesen 15) kerül.",
        "SUS: tíz állítás ötfokú skálán (1 = egyáltalán nem értek egyet, 5 = teljesen egyetértek). A páratlan állításoknál (érték − 1), a párosaknál (5 − érték) a pontszám, ezek összegét 2,5-del szorozzuk: 0–100. A pontszám nem százalék.",
        "Értelmezés (Bangor és mtsai, Sauro–Lewis): átlag ≈ 68; 70 fölött elfogadható, 50 alatt elfogadhatatlan. Mindig a megfigyelt feladatsikerrel együtt értelmezd (Feladatsiker lap).",
        "Két változat összevetésénél ugyanazok a résztvevők értékeljék mindkettőt (páros összehasonlítás), és a sorrendet résztvevőnként váltogasd. A statisztikai összevetést a tlx_sus notebook végzi.",
        "■ Példa: TLX – a KoboCella nyolc kezelője a jelenlegi kézi szerelésben és a kísérleti cellában; SUS – a VárosiBringa alkalmazás két prototípusa tizenkét résztvevővel (kézikönyv 11. fejezet).",
    ])
    sw = wb.create_sheet("Súlyok")
    cimsor(sw, "NASA-TLX súlyok (15 páros összehasonlítás győzelmei alskálánként)")
    tablazat(sw, 3, ["Résztvevő"] + ALSKALAK + ["Összesen (15 kell)"], [12] + [14] * 6 + [16],
             [[f"R{i + 1}"] + w for i, w in enumerate(W)], bemeneti_oszlopok=range(1, 8),
             kepletek={8: lambda r: f'=IF(COUNT(B{r}:G{r})=0,"",SUM(B{r}:G{r}))'}, uressor=NP - len(W))
    tl = wb.create_sheet("NASA-TLX")
    cimsor(tl, "NASA-TLX: két feltétel összevetése")
    u1 = tlx_blokk(tl, 3, "A feltétel: jelenlegi kézi szerelés", MAN)
    # a B blokk súlysorai ugyanazok a résztvevők
    r0b = u1 + 3
    u2 = tlx_blokk(tl, r0b, "B feltétel: KoboCella kísérleti cella", COB)
    rr = u2 + 2
    szoveg(tl.cell(row=rr, column=1), "Különbség (B − A) az átlagokban", felkov=True)
    for c in range(2, 10):
        col = get_column_letter(c)
        keplet(tl.cell(row=rr, column=c), f'=IF(OR({col}{u2}="",{col}{u1}=""),"",{col}{u2}-{col}{u1})', "+0.0;-0.0;0.0", True)
    ch = BarChart()
    ch.add_data(Reference(tl, min_col=1, max_col=7, min_row=u1, max_row=u1), from_rows=True, titles_from_data=True)
    ch.add_data(Reference(tl, min_col=1, max_col=7, min_row=u2, max_row=u2), from_rows=True, titles_from_data=True)
    ch.set_categories(Reference(tl, min_col=2, max_col=7, min_row=4, max_row=4))
    diagram_kozos(ch, "Alskálánkénti átlag (A: kézi, B: kísérleti cella)", None, "0–100", 20, 9)
    tl.add_chart(ch, f"A{rr + 3}")
    su = wb.create_sheet("SUS")
    cimsor(su, "SUS: két változat összevetése")
    for k, (t, adat) in enumerate([("1. prototípus", SUS1), ("2. prototípus", SUS2)]):
        r0 = 3 + k * (NP + 9)
        szoveg(su.cell(row=r0, column=1), t, felkov=True)
        fej = ["Résztvevő"] + [f"K{j + 1}" for j in range(10)] + ["SUS-pontszám"]
        kepl = {12: lambda r: (f'=IF(COUNT(B{r}:K{r})<10,"",2.5*((B{r}-1)+(5-C{r})+(D{r}-1)+(5-E{r})+(F{r}-1)+(5-G{r})'
                               f'+(H{r}-1)+(5-I{r})+(J{r}-1)+(5-K{r})))')}
        u = tablazat(su, r0 + 1, fej, [12] + [6] * 10 + [14], [[f"P{i + 1}"] + a for i, a in enumerate(adat)],
                     bemeneti_oszlopok=range(1, 12), kepletek=kepl, uressor=NP - len(adat), formatumok={12: "0.0"})
        for j, q in enumerate(SUS_KERDES):
            megjegyzes(su.cell(row=r0 + 1, column=2 + j), q)
        rg = f"L{r0 + 2}:L{u}"
        for i_, (tt, f, fmt) in enumerate([
                ("Résztvevők száma", f"=COUNT({rg})", "0"),
                ("Átlag", f'=IF(COUNT({rg})=0,"",AVERAGE({rg}))', "0.0"),
                ("Szórás", f'=IF(COUNT({rg})<2,"",STDEV({rg}))', "0.0"),
                ("95%-os konfidenciaintervallum félszélessége", f'=IF(COUNT({rg})<2,"",TINV(0.05,COUNT({rg})-1)*STDEV({rg})/SQRT(COUNT({rg})))', "0.0"),
                ("Elfogadhatóság (Bangor és mtsai, 2008)", f'=IF(COUNT({rg})=0,"",IF(AVERAGE({rg})>=70,"elfogadható",IF(AVERAGE({rg})<50,"elfogadhatatlan","határeset")))', None)]):
            szoveg(su.cell(row=u + 1 + i_, column=1), tt, felkov=True)
            su.merge_cells(start_row=u + 1 + i_, start_column=1, end_row=u + 1 + i_, end_column=6)
            keplet(su.cell(row=u + 1 + i_, column=12), f, fmt, True)
    fs = wb.create_sheet("Feladatsiker")
    cimsor(fs, "Feladatsiker (1 = segítség nélkül befejezte, 0 = nem)", "Feladatok: F1 kölcsönzés regisztrált felhasználóként, F2 dokkoló keresése, F3 vendégfizetés, F4 visszaadás.")
    for k, (t, adat) in enumerate([("1. prototípus", SIKER1), ("2. prototípus", SIKER2)]):
        c0 = 1 + k * 7
        szoveg(fs.cell(row=4, column=c0), t, felkov=True)
        fejlec(fs, 5, ["Résztvevő", "F1", "F2", "F3", "F4", "Sikerarány"], [11, 6, 6, 6, 6, 11], oszlop=c0)
        for i in range(NP):
            r = 6 + i
            a = adat[i] if i < len(adat) else None
            bemenet(fs.cell(row=r, column=c0), f"P{i + 1}" if a else None)
            for j in range(4):
                bemenet(fs.cell(row=r, column=c0 + 1 + j), a[j] if a else None)
            c1, c4 = get_column_letter(c0 + 1), get_column_letter(c0 + 4)
            keplet(fs.cell(row=r, column=c0 + 5), f'=IF(COUNT({c1}{r}:{c4}{r})=0,"",AVERAGE({c1}{r}:{c4}{r}))', "0%")
        c1, c4 = get_column_letter(c0 + 1), get_column_letter(c0 + 4)
        szoveg(fs.cell(row=7 + NP, column=c0), "Összesen", felkov=True)
        keplet(fs.cell(row=7 + NP, column=c0 + 5), f'=IF(COUNT({c1}6:{c4}{5 + NP})=0,"",SUM({c1}6:{c4}{5 + NP})/COUNT({c1}6:{c4}{5 + NP}))', "0%", True)
        for j in range(4):
            cj = get_column_letter(c0 + 1 + j)
            keplet(fs.cell(row=7 + NP, column=c0 + 1 + j), f'=IF(COUNT({cj}6:{cj}{5 + NP})=0,"",AVERAGE({cj}6:{cj}{5 + NP}))', "0%")
    return mentes(wb, "tlx_sus_sablon.xlsx")
