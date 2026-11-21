"""Morfológiai doboz (eszközlap: Morfológiai doboz)."""
import json

from _kozos import *  # noqa: F401,F403

D = json.loads((MAPPA.parents[1] / "_shared" / "adat" / "morf_kobo.json").read_text(encoding="utf-8"))
NF, NO, NP, NK = 10, 6, 60, 5


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Morfológiai doboz – sablon", [
        "■ Mire való? Részfunkciónként gyűjtött megoldások rendszerezett kombinálásával koncepciók előállítása (Zwicky).",
        "1. A „Doboz” lapon soronként egy részfunkció (kód: F1, F2 …), oszloponként a megoldási lehetőségek (legfeljebb 6). A megoldásokat úgy gyűjtsd, hogy egymástól eltérő működési elvekre épüljenek.",
        "2. A lap kiszámolja az elvi kombinációk számát (a megoldásszámok szorzata).",
        "3. Az „Összeférhetetlen” lapon add meg azokat a párokat, amelyek nem kombinálhatók (például F3.1 és F5.1 = a 3. részfunkció 1. és az 5. részfunkció 1. megoldása), indoklással.",
        "4. A „Koncepciók” lapon koncepciónként minden részfunkcióhoz válaszd ki a megoldás sorszámát. A lap kiírja a megoldást, és jelzi, ha a koncepció összeférhetetlen párt tartalmaz.",
        "5. Az összes összeférhető kombináció megszámlálását és a koncepciók változatosság szerinti kiválasztását a morfologiai_doboz notebook végzi.",
        "■ Példa: a KoboCella morfológiai doboza négy koncepcióval (kézikönyv 9. fejezet).",
    ])
    ws = wb.create_sheet("Doboz")
    cimsor(ws, "Morfológiai doboz", "A kódok (F1, F2 …) és a megoldások sorszámai együtt azonosítják a részmegoldásokat: például F3.2.")
    fej = ["Kód", "Részfunkció"] + [f"{j + 1}. megoldás" for j in range(NO)] + ["Megoldások száma"]
    sorok = [[f["kod"], f["nev"]] + f["opciok"] for f in D["funkciok"]]
    tablazat(ws, 4, fej, [7, 26] + [20] * NO + [11], sorok, bemeneti_oszlopok=range(1, 2 + NO + 1),
             kepletek={3 + NO: lambda r: f'=IF(B{r}="","",COUNTA(C{r}:{get_column_letter(2 + NO)}{r}))'},
             uressor=NF - len(sorok))
    for r in range(5, 5 + NF):
        for j in range(NO):
            ws.cell(row=r, column=3 + j).alignment = kozep
        ws.row_dimensions[r].height = 30
    rr = 6 + NF
    szoveg(ws.cell(row=rr, column=2), "Elvi kombinációk száma", felkov=True)
    keplet(ws.cell(row=rr, column=3), f"=PRODUCT({get_column_letter(3 + NO)}5:{get_column_letter(3 + NO)}{4 + NF})", "#,##0", felkov=True)
    megjegyzes(ws.cell(row=rr, column=3), "N = m1 · m2 · … · mn (a részfunkciónkénti megoldásszámok szorzata).")

    oe = wb.create_sheet("Összeférhetetlen")
    cimsor(oe, "Összeférhetetlen párok", "Kódformátum: részfunkció kódja, pont, a megoldás sorszáma (például F3.1).")
    tablazat(oe, 4, ["1. részmegoldás", "2. részmegoldás", "Indoklás"], [16, 16, 60],
             [list(p) for p in D["osszeferhetetlen"]], bemeneti_oszlopok=(1, 2, 3), uressor=NP - len(D["osszeferhetetlen"]))
    szoveg(oe.cell(row=6 + NP, column=1), "Párok száma", felkov=True)
    keplet(oe.cell(row=6 + NP, column=2), f'=COUNTIF(A5:A{4 + NP},"?*")')

    ko = wb.create_sheet("Koncepciók")
    cimsor(ko, "Koncepciók", "Koncepciónként minden részfunkcióhoz írd be a választott megoldás sorszámát (1–6).")
    konc = list(D["koncepciok"].items())
    ko.column_dimensions["A"].width = 7
    ko.column_dimensions["B"].width = 26
    fejlec(ko, 4, ["Kód", "Részfunkció"])
    for k in range(NK):
        c0 = 3 + 2 * k
        fejlec(ko, 4, ["Sorszám", "Választott megoldás"], [9, 24], oszlop=c0)
        nev = konc[k][0] if k < len(konc) else None
        bemenet(ko.cell(row=3, column=c0), nev)
        ko.merge_cells(start_row=3, start_column=c0, end_row=3, end_column=c0 + 1)
        valaszt = {x.split(".")[0]: int(x.split(".")[1]) for x in konc[k][1]} if k < len(konc) else {}
        for i in range(NF):
            r = 5 + i
            kodf = D["funkciok"][i]["kod"] if i < len(D["funkciok"]) else None
            bemenet(ko.cell(row=r, column=c0), valaszt.get(kodf))
            ko.cell(row=r, column=c0).alignment = kozep
            keplet(ko.cell(row=r, column=c0 + 1), f'=IF(OR({get_column_letter(c0)}{r}="",Doboz!$B{r}=""),"",INDEX(Doboz!$C{r}:${get_column_letter(2 + NO)}{r},1,{get_column_letter(c0)}{r}))')
        # kódlánc és ellenőrzés
        col = get_column_letter(c0)
        lanc = '=";"&' + '&";"&'.join(f'IF({col}{5 + i}="","",Doboz!$A{5 + i}&"."&{col}{5 + i})' for i in range(NF)) + '&";"'
        keplet(ko.cell(row=6 + NF, column=c0), lanc)
        ko.merge_cells(start_row=6 + NF, start_column=c0, end_row=6 + NF, end_column=c0 + 1)
        L = f"{col}{6 + NF}"
        keplet(ko.cell(row=7 + NF, column=c0),
               f"=SUMPRODUCT(('Összeférhetetlen'!$A$5:$A${4 + NP}<>\"\")*ISNUMBER(SEARCH(\";\"&'Összeférhetetlen'!$A$5:$A${4 + NP}&\";\",{L}))"
               f"*ISNUMBER(SEARCH(\";\"&'Összeférhetetlen'!$B$5:$B${4 + NP}&\";\",{L})))")
        keplet(ko.cell(row=8 + NF, column=c0), f'=IF({col}3="","",IF({col}{7 + NF}=0,"összeférhető","összeférhetetlen párt tartalmaz!"))')
        ko.merge_cells(start_row=8 + NF, start_column=c0, end_row=8 + NF, end_column=c0 + 1)
    for i in range(NF):
        r = 5 + i
        keplet(ko.cell(row=r, column=1), f'=IF(Doboz!A{r}="","",Doboz!A{r})')
        keplet(ko.cell(row=r, column=2), f'=IF(Doboz!B{r}="","",Doboz!B{r})')
    szoveg(ko.cell(row=6 + NF, column=2), "Kódlánc (segédszámítás)", felkov=True)
    szoveg(ko.cell(row=7 + NF, column=2), "Összeférhetetlen párok", felkov=True)
    szoveg(ko.cell(row=8 + NF, column=2), "Állapot", felkov=True)
    return mentes(wb, "morfologiai_doboz_sablon.xlsx")
