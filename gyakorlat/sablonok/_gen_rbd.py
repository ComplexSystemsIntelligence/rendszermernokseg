"""Megbízhatósági blokkdiagram és rendelkezésre állás (eszközlap: RBD)."""
from _kozos import *  # noqa: F401,F403

ELEMEK = [  # id, név, blokk, MTBF, MTTR, forrás
    ("E1", "kobot", "B1", 8000, 4, "beszállítói adatlap"),
    ("E2", "csavarozó egység", "B1", 2000, 1, "beszállítói adatlap"),
    ("E3", "csavaradagoló", "B1", 1500, 0.5, "csapat becslése"),
    ("E4", "lézerszkenner", "B1", 20000, 2, "beszállítói adatlap"),
    ("E5", "cellavezérlő", "B1", 30000, 3, "beszállítói adatlap"),
    ("E6", "UM-7 kézi szerelés (tartalék)", "B2", 490, 10, "csapat becslése: A = 0,98"),
]
BLOKK = [("B1", "KoboCella soros ága", "soros", None), ("B2", "UM-7 kézi tartalék", "soros", None)]
NE, NB = 25, 8


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Megbízhatósági blokkdiagram – sablon", [
        "■ Mire való? A rendszer megbízhatóságának és rendelkezésre állásának számítása az elemek adataiból, soros, párhuzamos és k-ból-n kapcsolással (kézikönyv 16. fejezet).",
        "1. Az „Elemek” lapon soronként egy elem: azonosító, név, a blokk, amelybe tartozik, MTBF (átlagos működési idő két hiba között, óra) és MTTR (átlagos javítási idő, óra), az adat forrása. Állandó meghibásodási rátát (exponenciális eloszlást) feltételezünk.",
        "2. Add meg a küldetési időt (például egy műszak), amelyre a megbízhatóságot számoljuk.",
        "3. A „Blokkok” lapon add meg a blokkok kapcsolását: soros (minden elem kell), párhuzamos (legalább egy elem kell) vagy k-ból-n (legalább k elem kell; azonos elemeket feltételez, az elemek átlagos értékével számol).",
        "4. A „Rendszer” lapon válaszd ki, hogyan kapcsolódnak a blokkok: sorosan vagy párhuzamosan.",
        "5. Figyelem: a képletek független meghibásodást feltételeznek. Közös okú hibák (közös táp, szoftver, karbantartás) esetén a párhuzamos ág számított előnye túlzó.",
        "■ Példa: a KoboCella termelési funkciója az UM-7 kézi tartalékkal (kézikönyv 16. fejezet).",
    ])
    e = wb.create_sheet("Elemek")
    cimsor(e, "Elemek")
    szoveg(e["A3"], "Küldetési idő t [óra]:", felkov=True); bemenet(e["C3"], 7.5)
    fej = ["Azonosító", "Elem", "Blokk", "MTBF [h]", "MTTR [h]", "Forrás", "λ [1/h]", "A", "R(t)", "Állásidő-hányad", "ln R", "ln(1−R)", "ln A", "ln(1−A)"]
    kepl = {7: lambda r: f'=IF(D{r}="","",1/D{r})', 8: lambda r: f'=IF(OR(D{r}="",E{r}=""),"",D{r}/(D{r}+E{r}))',
            9: lambda r: f'=IF(D{r}="","",EXP(-$C$3/D{r}))', 10: lambda r: f'=IF(H{r}="","",1-H{r})',
            11: lambda r: f'=IF(I{r}="","",LN(I{r}))', 12: lambda r: f'=IF(I{r}="","",LN(MAX(1-I{r},1E-15)))',
            13: lambda r: f'=IF(H{r}="","",LN(H{r}))', 14: lambda r: f'=IF(H{r}="","",LN(MAX(1-H{r},1E-15)))'}
    u = tablazat(e, 5, fej, [11, 30, 8, 10, 10, 26, 11, 10, 10, 13, 10, 10, 10, 10], [list(x) for x in ELEMEK],
                 bemeneti_oszlopok=(1, 2, 3, 4, 5, 6), kepletek=kepl, uressor=NE - len(ELEMEK),
                 formatumok={7: "0.0E+00", 8: "0.00000", 9: "0.00000", 10: "0.0E+00", 11: "0.0000", 12: "0.0000", 13: "0.0000", 14: "0.0000"})
    b = wb.create_sheet("Blokkok")
    cimsor(b, "Blokkok", "Típus: soros, párhuzamos vagy k-ból-n. A k-ból-n blokk azonos elemeket feltételez (az elemek átlagos R és A értékével).")
    rg = f"Elemek!$C$6:$C${u}"
    fej = ["Blokk", "Megnevezés", "Típus", "k", "Elemek száma", "R(t)", "A", "λ összeg [1/h] (soros)"]

    def rr(r, oszlop_ln, oszlop_ln1, ertek):
        return (f'=IF(OR(A{r}="",E{r}=0),"",IF(C{r}="soros",EXP(SUMIF({rg},A{r},Elemek!${oszlop_ln}$6:${oszlop_ln}${u})),'
                f'IF(C{r}="párhuzamos",1-EXP(SUMIF({rg},A{r},Elemek!${oszlop_ln1}$6:${oszlop_ln1}${u})),'
                f'1-BINOMDIST(D{r}-1,E{r},AVERAGEIF({rg},A{r},Elemek!${ertek}$6:${ertek}${u}),TRUE))))')
    kepl = {5: lambda r: f'=IF(A{r}="","",COUNTIF({rg},A{r}))', 6: lambda r: rr(r, "K", "L", "I"), 7: lambda r: rr(r, "M", "N", "H"),
            8: lambda r: f'=IF(OR(A{r}="",C{r}<>"soros"),"",SUMIF({rg},A{r},Elemek!$G$6:$G${u}))'}
    ub = tablazat(b, 4, fej, [9, 30, 13, 6, 12, 12, 12, 18], [list(x) + [None] * 4 for x in BLOKK], bemeneti_oszlopok=(1, 2, 3, 4),
                  kepletek=kepl, uressor=NB - len(BLOKK), formatumok={6: "0.000000", 7: "0.000000", 8: "0.0E+00"})
    legordulo(b, f"C5:C{ub}", ["soros", "párhuzamos", "k-ból-n"])
    s = wb.create_sheet("Rendszer")
    cimsor(s, "Rendszer: a blokkok kapcsolása")
    szoveg(s["A3"], "A blokkok kapcsolása:", felkov=True); bemenet(s["C3"], "párhuzamos")
    legordulo(s, "C3", ["soros", "párhuzamos"])
    fejlec(s, 5, ["Mutató", "", "Érték"], [44, 4, 16])
    br = f"Blokkok!$F$5:$F${ub}"; ba = f"Blokkok!$G$5:$G${ub}"
    # egyszerűbb, kompatibilis képletek segédoszlopokkal
    for i in range(NB):
        r = 5 + i
        keplet(b.cell(row=r, column=9), f'=IF(F{r}="","",LN(F{r}))', "0.0000")
        keplet(b.cell(row=r, column=10), f'=IF(F{r}="","",LN(MAX(1-F{r},1E-15)))', "0.0000")
        keplet(b.cell(row=r, column=11), f'=IF(G{r}="","",LN(G{r}))', "0.0000")
        keplet(b.cell(row=r, column=12), f'=IF(G{r}="","",LN(MAX(1-G{r},1E-15)))', "0.0000")
    fejlec(b, 4, ["ln R", "ln(1−R)", "ln A", "ln(1−A)"], [10, 10, 10, 10], oszlop=9)
    sorok = [
        ("Rendszer-megbízhatóság a küldetési időre, R(t)", f'=IF($C$3="soros",EXP(SUM(Blokkok!I5:I{ub})),1-EXP(SUM(Blokkok!J5:J{ub})))', "0.000000"),
        ("Rendszer rendelkezésre állása, A", f'=IF($C$3="soros",EXP(SUM(Blokkok!K5:K{ub})),1-EXP(SUM(Blokkok!L5:L{ub})))', "0.000000"),
        ("Éves üzemidő [h]", None, "0"),
        ("Várható éves állásidő [h]", "=(1-C7)*C8", "0.00"),
        ("Az első blokk várható éves meghibásodásszáma", "=IF(Blokkok!H5=\"\",\"\",Blokkok!H5*C8)", "0.0"),
        ("Az első blokk MTBF-je [h]", "=IF(Blokkok!H5=\"\",\"\",1/Blokkok!H5)", "0"),
    ]
    for k_, (t, f, fmt) in enumerate(sorok):
        r = 6 + k_
        szoveg(s.cell(row=r, column=1), t)
        if f is None:
            bemenet(s.cell(row=r, column=3), 3450, fmt)
        else:
            keplet(s.cell(row=r, column=3), f, fmt, True)
    szoveg(s["A13"], "A képletek független meghibásodást és állandó meghibásodási rátát feltételeznek.")
    return mentes(wb, "rbd_sablon.xlsx")
