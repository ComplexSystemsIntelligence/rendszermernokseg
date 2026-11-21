"""Tűréslánc-számítás (eszközlap: Tűréslánc)."""
from _kozos import *  # noqa: F401,F403

TAGOK = [("tömítés vastagsága", 2.50, 0.08, 1, "normális", 0, "beszállítói adatlap"),
         ("fedél horonymélysége", 2.20, 0.05, -1, "normális", 0, "rajz"),
         ("motorház tömítőperemének magassága", 0.30, 0.06, 1, "normális", 0, "rajz"),
         ("fedél síklapúsági eltérése", 0.00, 0.05, -1, "normális", 0, "rajz, geometriai tűrés")]
N = 15


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Tűréslánc – sablon", [
        "■ Mire való? Egy funkcionálisan fontos méret (rés, átfedés, összenyomódás) eredő tűrésének számítása a lánc tagjaiból: legrosszabb eset, statisztikus (RSS) összegzés, kiesési arány és folyamatképesség (kézikönyv 18. fejezet).",
        "1. A „Lánc” lapon soronként egy tag: megnevezés, névleges érték, szimmetrikus tűrés (±T), érzékenység (lineáris láncban +1 vagy −1; nemlineáris láncnál a parciális derivált), eloszlás (normális: T = szint × σ; egyenletes a ±T tartományban), a középérték várható eltolódása, forrás.",
        "2. Add meg a követelmény alsó és felső határát, és hogy a normális eloszlású tagoknál a tűrés hány szórásnak felel meg (szokásosan 3).",
        "3. Az eredmények: névleges érték, legrosszabb eset tartománya, RSS-tűrés, az eredő szórás és középérték (az eltolásokkal), Cp, Cpk és a határon kívüli arány normális közelítéssel.",
        "4. Az RSS a tagok függetlenségét és közel normális eredő eloszlást feltételez. Eltolt középértéknél, kevés tagnál vagy nem normális tagoknál ellenőrizd a turesek notebook Monte Carlo-szimulációjával.",
        "■ Példa: a KoboCella fedéltömítésének összenyomódása (kézikönyv 18. fejezet).",
    ])
    ws = wb.create_sheet("Lánc")
    cimsor(ws, "A tűréslánc tagjai")
    fej = ["Tag", "Névleges", "Tűrés ±T", "Érzékenység a", "Eloszlás", "Középérték-eltolás", "Forrás", "a × névleges", "|a| × T", "σ", "(a σ)²", "a × eltolás", "Hozzájárulás a szóráshoz"]
    kepl = {8: lambda r: f'=IF(A{r}="","",D{r}*B{r})', 9: lambda r: f'=IF(A{r}="","",ABS(D{r})*C{r})',
            10: lambda r: f'=IF(A{r}="","",IF(E{r}="egyenletes",C{r}/SQRT(3),C{r}/Eredmény!$C$6))',
            11: lambda r: f'=IF(A{r}="","",(D{r}*J{r})^2)', 12: lambda r: f'=IF(A{r}="","",D{r}*N(F{r}))',
            13: lambda r: f'=IF(OR(A{r}="",SUM($K$5:$K${4 + N})=0),"",K{r}/SUM($K$5:$K${4 + N}))'}
    u = tablazat(ws, 4, fej, [34, 10, 10, 13, 12, 14, 26, 12, 10, 10, 11, 11, 14], [list(t) for t in TAGOK],
                 bemeneti_oszlopok=(1, 2, 3, 4, 5, 6, 7), kepletek=kepl, uressor=N - len(TAGOK),
                 formatumok={2: "0.000", 3: "0.000", 6: "0.000", 8: "0.000", 9: "0.000", 10: "0.0000", 11: "0.000000", 12: "0.000", 13: "0%"})
    legordulo(ws, f"E5:E{u}", ["normális", "egyenletes"])
    e = wb.create_sheet("Eredmény")
    cimsor(e, "Eredmények")
    for k_, (t, v) in enumerate([("Alsó határ (LSL)", 0.40), ("Felső határ (USL)", 0.80), ("A tűrés hány szórásnak felel meg (normális tagok)", 3)]):
        szoveg(e.cell(row=4 + k_, column=1), t, felkov=True)
        bemenet(e.cell(row=4 + k_, column=3), v, "0.000" if k_ < 2 else "0")
    rg = f"Lánc!$H$5:$H${u}"
    sorok = [
        ("Névleges eredő érték", f"=SUM({rg})", "0.000"),
        ("Legrosszabb eset: ± tűrés", f"=SUM(Lánc!$I$5:$I${u})", "0.000"),
        ("Legrosszabb eset: alsó érték", "=C8-C9", "0.000"),
        ("Legrosszabb eset: felső érték", "=C8+C9", "0.000"),
        ("Legrosszabb eset: teljesíti a követelményt?", '=IF(AND(C10>=C4,C11<=C5),"igen","nem")', None),
        ("RSS: ± tűrés (3σ)", f"=3*SQRT(SUM(Lánc!$K$5:$K${u}))", "0.000"),
        ("Eredő szórás σ", f"=SQRT(SUM(Lánc!$K$5:$K${u}))", "0.0000"),
        ("Eredő középérték (eltolásokkal)", f"=C8+SUM(Lánc!$L$5:$L${u})", "0.000"),
        ("Cp", "=IF(C14=0,\"\",(C5-C4)/(6*C14))", "0.00"),
        ("Cpk", "=IF(C14=0,\"\",MIN(C5-C15,C15-C4)/(3*C14))", "0.00"),
        ("Határon kívüli arány (normális közelítés)", "=IF(C14=0,\"\",NORMSDIST((C4-C15)/C14)+1-NORMSDIST((C5-C15)/C14))", "0.000E+00"),
        ("Határon kívüli darab egymillióból", "=IF(C18=\"\",\"\",C18*1000000)", "0.0"),
        ("Legrosszabb esethez szükséges tűrésszűkítés (szorzó)", "=IF(C9=0,\"\",MIN(1,MIN(C5-C8,C8-C4)/C9))", "0.00"),
    ]
    for k_, (t, f, fmt) in enumerate(sorok):
        r = 8 + k_
        szoveg(e.cell(row=r, column=1), t)
        keplet(e.cell(row=r, column=3), f, fmt, True)
    e.column_dimensions["A"].width = 52; e.column_dimensions["C"].width = 14
    szoveg(e["A22"], "A tűrésszűkítés szorzója azt mutatja, hányszorosára kellene csökkenteni minden tűrést, hogy a legrosszabb eset is a határon belül maradjon.")
    return mentes(wb, "turesek_sablon.xlsx")
