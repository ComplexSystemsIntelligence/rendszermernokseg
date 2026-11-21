"""Sorbanállási modellek (eszközlap: Sorbanállási modellek)."""
from _kozos import *  # noqa: F401,F403

VALT = [("hajtáslánc, alapállapot (M/M/1)", 40 / 7.5, 9, 1, 1, 1),
        ("hajtáslánc, mért kiszolgálási szórás", 40 / 7.5, 9, 1, 1, 0.5),
        ("fékjavítás, alapállapot (2 szerelő)", 40 / 7.5, 14, 2, 1, 1),
        ("mosás + lánctisztítás, nyári csúcs", 55 / 7.5, 7, 1, 1, 1),
        ("fékjavítás, nyári csúcs", 55 / 7.5, 14, 2, 1, 1),
        ("mosás, csúcs, időpontfoglalással", 55 / 7.5, 7, 1, 0.5, 0.5)]
NV = 20


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Sorbanállási modellek – sablon", [
        "■ Mire való? Egy kiszolgáló egység (gép, munkahely, ügyfélszolgálat) várakozási idejének és sorhosszának becslése az érkezési intenzitásból, a kiszolgálási időből, a kiszolgálók számából és a változékonyságból (kézikönyv 21. fejezet; Lakatos: Termelési rendszerek, 8.3; Kendall, 1953; Kingman, 1961; Hopp és Spearman, 2008).",
        "1. Az „M/M/c” lap pontos eredményt ad Poisson-érkezésre és exponenciális kiszolgálási időre: kihasználtság, a várakozás valószínűsége (Erlang C), a sorban és a rendszerben töltött idő, a sor- és a rendszerhossz, és annak valószínűsége, hogy a várakozás meghalad egy adott időt.",
        "2. A „Változatok” lapon soronként egy helyzet: érkezési intenzitás (darab/óra), átlagos kiszolgálási idő (perc), kiszolgálók száma, az érkezések közötti idő és a kiszolgálási idő relatív szórása (ca, cs). A lap a Hopp–Spearman-féle G/G/c közelítéssel számol: Wq ≈ (ca² + cs²)/2 · ρ^(√(2(c+1)) − 1) / (c(1 − ρ)) · ts; egy kiszolgálónál ez Kingman közelítése, exponenciális eloszlásoknál M/M/1-re pontos.",
        "3. A relatív szórás (CV) a szórás és az átlag hányadosa: véletlen (Poisson) érkezésnél ca = 1, időpontfoglalásnál kisebb; exponenciális kiszolgálásnál cs = 1, szabványos munkánál 0,3–0,5 körüli is lehet. Mérésből számold!",
        "4. A „Kihasználtság” lap megmutatja, hogyan nő a várakozás a kihasználtsággal egy választott kiszolgálási időnél és változékonyságnál.",
        "5. A modellek stacionárius állapotra érvényesek (hosszú távon állandó intenzitások, ρ < 1). Napon belül változó érkezésnél, véges időtávnál vagy összetett útvonalaknál szimuláció kell (sorbanallas notebook).",
        "■ Példa: a VárosiBringa javítóműhelye (kézikönyv 19. és 21. fejezet).",
    ])
    m = wb.create_sheet("M-M-c")
    cimsor(m, "M/M/c: Poisson-érkezés, exponenciális kiszolgálás, c kiszolgáló")
    par = [("Érkezési intenzitás λ [db/óra]", 40 / 7.5, "0.000"), ("Átlagos kiszolgálási idő [perc]", 9, "0.00"),
           ("Kiszolgálók száma c", 1, "0"), ("Várakozási időhatár t [perc] a valószínűséghez", 30, "0")]
    for i, (t, v, fmt) in enumerate(par):
        szoveg(m.cell(row=3 + i, column=1), t, felkov=True)
        bemenet(m.cell(row=3 + i, column=2), v, fmt)
    fejlec(m, 3, ["k", "a^k / k!"], [6, 14], oszlop=5)
    for k in range(50):
        r = 4 + k
        szoveg(m.cell(row=r, column=5), k)
        keplet(m.cell(row=r, column=6), f'=IF(E{r}<$B$5,$B$10^E{r}/FACT(E{r}),0)', "0.0000E+00")
    sor = [
        ("Kiszolgálási intenzitás μ [db/óra]", '=IF(B4<=0,"",60/B4)', "0.000"),
        ("Felajánlott forgalom a = λ/μ", '=IF(B9="","",B3/B9)', "0.000"),
        ("Kihasználtság ρ = λ/(c·μ)", '=IF(B10="","",B10/B5)', "0.0%"),
        ("Állapot", '=IF(B11="","",IF(B11>=1,"INSTABIL: a sor korlátlanul nő (ρ ≥ 1)","stabil"))', None),
        ("P0 (üres rendszer valószínűsége)", '=IF(OR(B11="",B11>=1),"",1/(SUM(F4:F53)+B10^B5/(FACT(B5)*(1-B11))))', "0.0000"),
        ("A várakozás valószínűsége (Erlang C)", '=IF(B13="","",B10^B5/(FACT(B5)*(1-B11))*B13)', "0.0%"),
        ("Átlagos sorhossz Lq", '=IF(B14="","",B14*B11/(1-B11))', "0.00"),
        ("Átlagos várakozás a sorban Wq [perc]", '=IF(B15="","",B15/B3*60)', "0.0"),
        ("Átlagos idő a rendszerben W [perc]", '=IF(B16="","",B16+B4)', "0.0"),
        ("Átlagos szám a rendszerben L = λW", '=IF(B17="","",B3*B17/60)', "0.00"),
        ("P(várakozás > t)", '=IF(B14="","",B14*EXP(-(B5*B9-B3)*B6/60))', "0.0%"),
    ]
    for k, (t, f, fmt) in enumerate(sor):
        szoveg(m.cell(row=9 + k, column=1), t)
        keplet(m.cell(row=9 + k, column=2), f, fmt, True)
    m.column_dimensions["A"].width = 46; m.column_dimensions["B"].width = 16
    szoveg(m["A21"], "Ellenőrzés a Little-törvénnyel: L = Lq + a. Az E–F oszlop a P0 számításának segédtáblája (c ≤ 50).")
    keplet(m["B22"], '=IF(B18="","",B18-(B15+B10))', "0.0000")
    szoveg(m["A22"], "L − (Lq + a) (0 kell legyen)")

    v = wb.create_sheet("Változatok")
    cimsor(v, "Változatok: G/G/c közelítés (Hopp és Spearman)")
    fej = ["Változat", "λ [db/óra]", "Kiszolgálási idő ts [perc]", "Kiszolgálók c", "ca", "cs", "Kihasználtság ρ",
           "Wq [perc]", "W [perc]", "Lq", "L", "Wq / ts", "Megjegyzés"]
    kepl = {7: lambda r: f'=IF(OR(A{r}="",N(D{r})=0),"",B{r}*C{r}/60/D{r})',
            8: lambda r: f'=IF(OR(G{r}="",G{r}>=1),"",(E{r}^2+F{r}^2)/2*G{r}^(SQRT(2*(D{r}+1))-1)/(D{r}*(1-G{r}))*C{r})',
            9: lambda r: f'=IF(H{r}="","",H{r}+C{r})',
            10: lambda r: f'=IF(H{r}="","",B{r}*H{r}/60)',
            11: lambda r: f'=IF(I{r}="","",B{r}*I{r}/60)',
            12: lambda r: f'=IF(H{r}="","",H{r}/C{r})',
            13: lambda r: f'=IF(G{r}="","",IF(G{r}>=1,"instabil (ρ ≥ 1)",IF(G{r}>0.85,"nagy kihasználtság: érzékeny a zavarokra","")))'}
    tablazat(v, 3, fej, [38, 10, 12, 10, 7, 7, 12, 10, 10, 8, 8, 9, 34], [list(x) for x in VALT], bemeneti_oszlopok=(1, 2, 3, 4, 5, 6),
             kepletek=kepl, uressor=NV - len(VALT), formatumok={2: "0.000", 3: "0.0", 4: "0", 5: "0.00", 6: "0.00", 7: "0.0%",
                                                                8: "0.0", 9: "0.0", 10: "0.00", 11: "0.00", 12: "0.00"})
    szoveg(v.cell(row=5 + NV, column=1), "A közelítés egy kiszolgálónál Kingman képlete; több kiszolgálónál Sakasegawa közelítésére épül, nagy kihasználtságnál pontosabb. M/M/c esetben az „M-M-c” lap pontos értékével összevethető.")
    v.merge_cells(start_row=5 + NV, start_column=1, end_row=6 + NV, end_column=13)

    k = wb.create_sheet("Kihasználtság")
    cimsor(k, "A várakozás a kihasználtság függvényében")
    for i, (t, val, fmt) in enumerate([("Kiszolgálási idő ts [perc]", 9, "0.0"), ("Kiszolgálók c", 1, "0"), ("ca", 1, "0.00"), ("cs", 0.5, "0.00")]):
        szoveg(k.cell(row=3 + i, column=1), t, felkov=True)
        bemenet(k.cell(row=3 + i, column=2), val, fmt)
    fejlec(k, 8, ["ρ", "Wq [perc], ca = cs = 1", "Wq [perc], a megadott ca, cs", "Wq / ts (megadott)"], [8, 18, 22, 16])
    rhos = [0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.92, 0.94, 0.96, 0.98]
    for i, rho in enumerate(rhos):
        r = 9 + i
        szoveg(k.cell(row=r, column=1), rho); k.cell(row=r, column=1).number_format = "0.00"
        keplet(k.cell(row=r, column=2), f"=A{r}^(SQRT(2*($B$4+1))-1)/($B$4*(1-A{r}))*$B$3", "0.0")
        keplet(k.cell(row=r, column=3), f"=($B$5^2+$B$6^2)/2*A{r}^(SQRT(2*($B$4+1))-1)/($B$4*(1-A{r}))*$B$3", "0.0")
        keplet(k.cell(row=r, column=4), f"=C{r}/$B$3", "0.00")
    ch = LineChart()
    ch.add_data(Reference(k, min_col=2, max_col=3, min_row=8, max_row=8 + len(rhos)), titles_from_data=True)
    ch.set_categories(Reference(k, min_col=1, min_row=9, max_row=8 + len(rhos)))
    diagram_kozos(ch, "Átlagos várakozás a sorban", "kihasználtság ρ", "perc", 18, 9)
    k.add_chart(ch, "F3")
    return mentes(wb, "sorbanallas_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
