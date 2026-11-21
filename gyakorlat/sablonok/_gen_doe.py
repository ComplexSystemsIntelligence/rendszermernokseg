"""2^3 teljes faktoros kísérlet kiértékelése (eszközlap: Kísérlettervezés)."""
from _kozos import *  # noqa: F401,F403
import itertools

TENYEZO = [("A", "végső fordulatszám", "alacsony", "magas", "tervezési"),
           ("B", "csavarozási stratégia", "egylépcsős", "kétlépcsős", "tervezési"),
           ("C", "bitbetét állapota", "új", "kopott", "zaj")]
Y = {(-1, -1, -1): [4.036, 4.077], (-1, -1, 1): [3.872, 3.952], (-1, 1, -1): [3.978, 3.947], (-1, 1, 1): [3.913, 3.956],
     (1, -1, -1): [4.145, 4.115], (1, -1, 1): [3.973, 3.949], (1, 1, -1): [4.058, 4.087], (1, 1, 1): [4.046, 4.045]}
SORREND = [[5, 12], [2, 9], [14, 7], [11, 1], [8, 16], [3, 13], [10, 6], [15, 4]]
HATAS = ["A", "B", "C", "AB", "AC", "BC", "ABC"]


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Kísérlettervezés: 2³ teljes faktoros kísérlet – sablon", [
        "■ Mire való? Három tényező főhatásának és kölcsönhatásainak becslése nyolc beállításban, legfeljebb három ismétléssel; a tervezési és a zajtényezők kölcsönhatásából robusztus beállítás választása (kézikönyv 18. fejezet).",
        "1. A „Tényezők” lapon add meg a három tényező nevét, alsó (−1) és felső (+1) szintjét és típusát (tervezési vagy zaj).",
        "2. A „Kísérlet” lapon a nyolc beállítás kódolt szintjei adottak. Futtasd a kísérleteket a „Sorrend” oszlopok szerinti véletlen sorrendben, és írd be a mért válaszokat (1–3 ismétlés).",
        "3. A „Hatások” lap a főhatásokat és a kölcsönhatásokat a beállítások átlagaiból számítja (hatás = átlag a +1 szinten − átlag a −1 szinten). Ismétlés esetén a kísérleti hiba szórásából a hatások standard hibáját és t-értékét is megadja.",
        "4. A „Kölcsönhatás” lap a két tényező szintjeinek kombinációira vett átlagokat mutatja; egy tervezési és egy zajtényező kölcsönhatása a robusztusság kulcsa.",
        "5. Részletesebb elemzés (Pareto-ábra, robusztus beállítás keresése): doe notebook.",
        "■ Példa: a KoboCella csavarozási nyomatéka, két ismétléssel (kézikönyv 18. fejezet).",
    ])
    t = wb.create_sheet("Tényezők")
    cimsor(t, "Tényezők és szintek")
    tablazat(t, 3, ["Kód", "Tényező", "Alsó szint (−1)", "Felső szint (+1)", "Típus"], [7, 30, 18, 18, 12], [list(x) for x in TENYEZO], bemeneti_oszlopok=(2, 3, 4, 5))
    legordulo(t, "E4:E6", ["tervezési", "zaj"])
    szoveg(t["A8"], "A válasz megnevezése és mértékegysége:", felkov=True); bemenet(t["D8"], "nyomaték [Nm]")
    szoveg(t["A9"], "Célérték (ha van):", felkov=True); bemenet(t["D9"], 4.0, "0.000")
    k = wb.create_sheet("Kísérlet")
    cimsor(k, "A kísérleti terv és a mért válaszok")
    fej = ["Beállítás", "A", "B", "C", "Sorrend 1", "Sorrend 2", "Sorrend 3", "y1", "y2", "y3", "Átlag", "Szórás", "n"]
    sor = []
    for i, (a, b, c) in enumerate(itertools.product([-1, 1], repeat=3)):
        y = Y[(a, b, c)]
        sor.append([i + 1, a, b, c, SORREND[i][0], SORREND[i][1], None, y[0], y[1], None, None, None, None])
    kepl = {11: lambda r: f'=IF(COUNT(H{r}:J{r})=0,"",AVERAGE(H{r}:J{r}))', 12: lambda r: f'=IF(COUNT(H{r}:J{r})<2,"",STDEV(H{r}:J{r}))',
            13: lambda r: f"=COUNT(H{r}:J{r})"}
    tablazat(k, 3, fej, [10, 6, 6, 6, 10, 10, 10, 9, 9, 9, 10, 10, 6], sor, bemeneti_oszlopok=(5, 6, 7, 8, 9, 10), kepletek=kepl,
             formatumok={8: "0.000", 9: "0.000", 10: "0.000", 11: "0.0000", 12: "0.0000"})
    for r in range(4, 12):
        for c in (2, 3, 4):
            k.cell(row=r, column=c).alignment = kozep
    # segédoszlopok: kölcsönhatás-oszlopok
    fejlec(k, 3, ["AB", "AC", "BC", "ABC"], [6, 6, 6, 6], oszlop=15)
    for r in range(4, 12):
        for j, f in enumerate([f"=B{r}*C{r}", f"=B{r}*D{r}", f"=C{r}*D{r}", f"=B{r}*C{r}*D{r}"]):
            keplet(k.cell(row=r, column=15 + j), f, "0")
    h = wb.create_sheet("Hatások")
    cimsor(h, "Főhatások és kölcsönhatások")
    oszl = {"A": "B", "B": "C", "C": "D", "AB": "O", "AC": "P", "BC": "Q", "ABC": "R"}
    szoveg(h["A3"], "Összes mérés N:", felkov=True); keplet(h["C3"], "=SUM(Kísérlet!M4:M11)", "0", True)
    szoveg(h["A4"], "A kísérleti hiba becsült szórása s (az ismétlésekből):", felkov=True)
    keplet(h["C4"], '=IF(C3<=8,"",SQRT(SUMPRODUCT((Kísérlet!M4:M11-1),Kísérlet!L4:L11^2)/(C3-8)))', "0.0000", True)
    szoveg(h["A5"], "Szabadsági fok:", felkov=True); keplet(h["C5"], "=IF(C3<=8,\"\",C3-8)", "0", True)
    szoveg(h["A6"], "t kritikus érték (5%, kétoldali):", felkov=True); keplet(h["C6"], '=IF(C5="","",TINV(0.05,C5))', "0.000", True)
    fejlec(h, 8, ["Hatás", "Becslés", "|Becslés|", "Standard hiba", "t-érték", "Szignifikáns (5%)?"], [10, 12, 12, 14, 10, 18])
    for i, nev in enumerate(HATAS):
        r = 9 + i
        col = oszl[nev]
        szoveg(h.cell(row=r, column=1), nev)
        keplet(h.cell(row=r, column=2), f"=SUMPRODUCT(Kísérlet!{col}4:{col}11,Kísérlet!K4:K11)/4", "+0.0000;-0.0000;0.0000")
        keplet(h.cell(row=r, column=3), f"=ABS(B{r})", "0.0000")
        keplet(h.cell(row=r, column=4), '=IF($C$4="","",2*$C$4/SQRT($C$3))', "0.0000")
        keplet(h.cell(row=r, column=5), f'=IF(D{r}="","",B{r}/D{r})', "0.00")
        keplet(h.cell(row=r, column=6), f'=IF(E{r}="","",IF(ABS(E{r})>$C$6,"igen","nem"))')
    szoveg(h["A17"], "Átlag (főátlag):", felkov=True); keplet(h["C17"], "=AVERAGE(Kísérlet!K4:K11)", "0.0000", True)
    ch = BarChart()
    ch.add_data(Reference(h, min_col=2, min_row=8, max_row=15), titles_from_data=True)
    ch.set_categories(Reference(h, min_col=1, min_row=9, max_row=15))
    diagram_kozos(ch, "Hatások", "hatás", "becslés", 16, 8)
    h.add_chart(ch, "H3")
    kh = wb.create_sheet("Kölcsönhatás")
    cimsor(kh, "Kétszintű kölcsönhatási táblák (átlagok)")
    parok = [("A", "B", "B", "C"), ("A", "C", "B", "D"), ("B", "C", "C", "D")]
    r0 = 3
    for p1, p2, c1, c2 in parok:
        szoveg(kh.cell(row=r0, column=1), f"{p1} × {p2}", felkov=True)
        fejlec(kh, r0 + 1, [f"{p1} \\ {p2}", "−1", "+1", "Különbség (+1 − −1)"], [10, 10, 10, 20])
        for i, s1 in enumerate([-1, 1]):
            r = r0 + 2 + i
            szoveg(kh.cell(row=r, column=1), s1)
            for j, s2 in enumerate([-1, 1]):
                keplet(kh.cell(row=r, column=2 + j), f"=AVERAGEIFS(Kísérlet!$K$4:$K$11,Kísérlet!${c1}$4:${c1}$11,{s1},Kísérlet!${c2}$4:${c2}$11,{s2})", "0.0000")
            keplet(kh.cell(row=r, column=4), f"=C{r}-B{r}", "+0.0000;-0.0000;0.0000")
        r0 += 6
    szoveg(kh.cell(row=r0, column=1), "Robusztus beállítás: az a tervezési szint, amelynél a zajtényező hatása (különbség) a legkisebb abszolút értékű.")
    return mentes(wb, "doe_sablon.xlsx")
