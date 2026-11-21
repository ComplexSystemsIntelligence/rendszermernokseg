"""Hibafa: kapuszintű számítás és minimális vágathalmazok (eszközlap: Hibafa)."""
from _kozos import *  # noqa: F401,F403

ALAP = [("E1", "a kezelő a közös térben van a hiba idején", 0.3, "műszakmegfigyelés: a ciklusidő kb. 30%-a"),
        ("E2", "a lézerszkenner nem érzékel (veszélyes, fel nem fedezett hiba)", 0.01, "becslés, évi érték"),
        ("E3", "a biztonsági vezérlés veszélyes hibája", 0.001, "becslés, évi érték"),
        ("E4", "az erőhatárolás hibája", 0.005, "becslés, évi érték")]
KAPU = [("G1", "a kezelőt teljes sebességű kobotkar éri (csúcsesemény)", "ÉS", ["E1", "G2", "G3"]),
        ("G2", "nincs sebességcsökkentés", "VAGY", ["E2", "E3"]),
        ("G3", "nincs erőhatárolás", "VAGY", ["E4", "E3"])]
VAGAT = [["E1", "E3"], ["E1", "E2", "E4"]]
NA, NK, NV, BE = 30, 20, 15, 5


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Hibafa – sablon", [
        "■ Mire való? Egy nem kívánt csúcsesemény okainak logikai lebontása ÉS- és VAGY-kapukkal, és a csúcsesemény valószínűségének becslése (kézikönyv 16. fejezet; NUREG-0492).",
        "1. Az „Alapesemények” lapon add meg az alapeseményeket azonosítóval (E…), leírással, valószínűséggel (ugyanarra az időszakra!) és az adat forrásával.",
        "2. A „Kapuk” lapon soronként egy kapu: azonosító (G…), leírás, típus (ÉS / VAGY) és legfeljebb öt bemenet (alapesemény vagy másik kapu azonosítója). Az első sor legyen a csúcsesemény.",
        "3. A kapuk valószínűségét a lap független eseményeket feltételezve számolja: ÉS = szorzat, VAGY = 1 − Π(1 − p). Ha egy alapesemény több ágban is szerepel (ismétlődő esemény), ez a számítás hibás, és általában alábecsül!",
        "4. Ismétlődő eseménynél a „Vágathalmazok” lapon add meg a minimális vágathalmazokat (a hibafa notebook kiszámítja őket), és a csúcsesemény valószínűségét azokból becsüld.",
        "■ Példa: a KoboCella biztonsági csúcseseménye; az E3 ismétlődő esemény (kézikönyv 16. fejezet).",
    ])
    a = wb.create_sheet("Alapesemények")
    cimsor(a, "Alapesemények")
    ua = tablazat(a, 3, ["Azonosító", "Leírás", "Valószínűség", "Forrás"], [11, 56, 14, 40], [list(x) for x in ALAP],
                  bemeneti_oszlopok=(1, 2, 3, 4), uressor=NA - len(ALAP), formatumok={3: "0.0E+00"})
    k = wb.create_sheet("Kapuk")
    cimsor(k, "Kapuk", "Bemenet: alapesemény (E…) vagy kapu (G…) azonosítója. A kapuk sorrendje tetszőleges, de kör nem lehet.")
    fej = ["Azonosító", "Leírás", "Típus"] + [f"Bemenet {i + 1}" for i in range(BE)] + ["Valószínűség (független)"] + [f"p{i + 1}" for i in range(BE)] + [f"1−p{i + 1}" for i in range(BE)]
    uk = 4 + NK
    lp = lambda c: (f'IFERROR(INDEX(Alapesemények!$C$4:$C${ua},MATCH({c},Alapesemények!$A$4:$A${ua},0)),'
                    f'IFERROR(INDEX($I$5:$I${uk},MATCH({c},$A$5:$A${uk},0)),""))')
    kepl = {9: lambda r: f'=IF(OR(A{r}="",C{r}=""),"",IF(C{r}="ÉS",PRODUCT(J{r}:N{r}),1-PRODUCT(O{r}:S{r})))'}
    for i in range(BE):
        col = get_column_letter(4 + i)
        kepl[10 + i] = (lambda col: (lambda r: f'=IF({col}{r}="","",{lp(f"{col}{r}")})'))(col)
        pc = get_column_letter(10 + i)
        kepl[15 + i] = (lambda pc: (lambda r: f'=IF({pc}{r}="","",1-{pc}{r})'))(pc)
    sor = [[g, l, t] + (be + [None] * BE)[:BE] + [None] * (1 + 2 * BE) for g, l, t, be in KAPU]
    tablazat(k, 4, fej, [10, 48, 8] + [11] * BE + [16] + [9] * (2 * BE), sor, bemeneti_oszlopok=tuple(range(1, 4 + BE)),
             kepletek=kepl, uressor=NK - len(KAPU), formatumok={9: "0.000E+00", **{10 + i: "0.0E+00" for i in range(2 * BE)}})
    legordulo(k, f"C5:C{uk}", ["ÉS", "VAGY"])
    v = wb.create_sheet("Vágathalmazok")
    cimsor(v, "Minimális vágathalmazok", "A hibafa notebook kiszámítja őket. Egy sor egy vágathalmaz, legfeljebb öt eseménnyel.")
    fej = ["Vágathalmaz"] + [f"Esemény {i + 1}" for i in range(BE)] + ["Valószínűség (szorzat)", "Hozzájárulás", "1 − P"] + [f"p{i + 1}" for i in range(BE)]
    uv = 4 + NV
    kepl = {7: lambda r: f'=IF(B{r}="","",PRODUCT(J{r}:N{r}))', 8: lambda r: f'=IF(G{r}="","",G{r}/SUM($G$5:$G${uv}))',
            9: lambda r: f'=IF(G{r}="","",1-G{r})'}
    for i in range(BE):
        col = get_column_letter(2 + i)
        kepl[10 + i] = (lambda col: (lambda r: f'=IF({col}{r}="","",IFERROR(INDEX(Alapesemények!$C$4:$C${ua},MATCH({col}{r},Alapesemények!$A$4:$A${ua},0)),""))'))(col)
    tablazat(v, 4, fej, [13] + [11] * BE + [20, 13, 9] + [9] * BE, [[f"C{i + 1}"] + (c + [None] * BE)[:BE] + [None] * (3 + BE) for i, c in enumerate(VAGAT)],
             bemeneti_oszlopok=tuple(range(1, 2 + BE)), kepletek=kepl, uressor=NV - len(VAGAT),
             formatumok={7: "0.000E+00", 8: "0%", 9: "0.000000", **{10 + i: "0.0E+00" for i in range(BE)}})
    r0 = uv + 2
    for k_, (t, f, fmt) in enumerate([
            ("Csúcsesemény: ritka esemény közelítés (Σ vágathalmaz)", f"=SUM(G5:G{uv})", "0.000E+00"),
            ("Csúcsesemény: felső korlát 1 − Π(1 − P(vágathalmaz))", f"=1-PRODUCT(I5:I{uv})", "0.000E+00"),
            ("Csúcsesemény a kapuszintű (független) számítással", "=Kapuk!I5", "0.000E+00"),
            ("Arány: vágathalmaz / kapuszintű", f"=IF(C{r0 + 2}=0,\"\",C{r0}/C{r0 + 2})", "0.0"),
            ("Egyelemű vágathalmazok (egypontos hibák) száma", f'=SUMPRODUCT((B5:B{uv}<>"")*(C5:C{uv}=""))', "0")]):
        szoveg(v.cell(row=r0 + k_, column=1), t, felkov=True)
        v.merge_cells(start_row=r0 + k_, start_column=1, end_row=r0 + k_, end_column=2)
        keplet(v.cell(row=r0 + k_, column=3), f, fmt, True)
    return mentes(wb, "hibafa_sablon.xlsx")
