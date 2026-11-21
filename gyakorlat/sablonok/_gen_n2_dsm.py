"""N²-diagram és tervezési struktúramátrix (DSM) (eszközlap: N²-diagram és DSM)."""
import json

from _kozos import *  # noqa: F401,F403

D = json.loads((MAPPA.parents[1] / "_shared" / "adat" / "dsm_bringa.json").read_text(encoding="utf-8"))
MODUL = {"ÁT": "platform", "H": "platform", "APP": "platform", "F": "platform", "D": "dokkoló", "TÖ": "dokkoló",
         "DV": "dokkoló", "V": "kerékpár", "Z": "kerékpár", "T": "kerékpár", "A": "kerékpár", "M": "kerékpár"}
N = 20  # kapacitás
N2_ELEM = ["kobot és megfogó", "csavarozó egység", "munkaasztal, adagolás", "biztonsági alrendszer", "cellavezérlés, HMI", "operátor"]
N2_IF = {(0, 1): "pozíció kész", (0, 4): "robotállapot", (1, 4): "nyomaték, szög", (1, 0): "meghúzás kész",
         (2, 0): "alkatrész jelen", (2, 1): "csavar adagolva", (3, 0): "sebességkorlát, stop", (3, 1): "stop",
         (3, 4): "zónaállapot", (4, 0): "programszám, start", (4, 1): "nyomatékprogram", (4, 5): "hibakód, utasítás",
         (5, 2): "alkatrész behelyezése", (5, 4): "nyugtázás, start", (5, 3): "belépés a zónába"}


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "N²-diagram és DSM – sablon", [
        "■ Mire való? A rendszerelemek közötti interfészek azonosítása (N²-diagram) és a kapcsolatok mátrixos elemzése modulok kialakításához (DSM).",
        "1. Az „N2” lapon az átlóba az alrendszerek kerülnek. Az i-edik sor j-edik cellájába írd, mit ad át az i-edik elem a j-ediknek (kimenetek a sorokban, bemenetek az oszlopokban). Üres cella: nincs közvetlen interfész.",
        "2. Az „Elemek” lapon sorold fel a DSM elemeit kóddal és névvel, és add meg, melyik modulba sorolod őket (a modulokat a notebook klaszterezése is javasolja).",
        "3. A „DSM” lapon 1-est írj oda, ahol két elem között kapcsolat van. Kölcsönös (szimmetrikus) kapcsolatoknál mindkét cellát töltsd ki; az aszimmetria-számláló jelzi az eltéréseket.",
        "4. Az összesítés kiszámítja a kapcsolatok számát, a modulokon belüli és a modulok közötti kapcsolatokat. A modulok közötti kapcsolatok a modulinterfészek: ezekhez interfészgazdát kell rendelni.",
        "5. A klaszterezést (a sorrend átrendezését) és a modularitási mérőszámot az n2_dsm notebook végzi el.",
        "■ Példa: a KoboCella N²-diagramja és a VárosiBringa DSM-je (kézikönyv 8. fejezet).",
    ])
    n2 = wb.create_sheet("N2")
    cimsor(n2, "N²-diagram", "Átló: alrendszerek. Sor: az alrendszer kimenetei. Oszlop: az alrendszer bemenetei.")
    k = 8
    for i in range(k):
        n2.column_dimensions[get_column_letter(2 + i)].width = 18
        n2.row_dimensions[5 + i].height = 34
        for j in range(k):
            c = n2.cell(row=5 + i, column=2 + j)
            if i == j:
                bemenet(c, N2_ELEM[i] if i < len(N2_ELEM) else None)
                c.font = Font(name="Arial", size=10, bold=True, color="0000FF")
            else:
                bemenet(c, N2_IF.get((i, j)))
            c.alignment = kozep
    fejlec(n2, 4, ["Sor"] + [f"{j + 1}." for j in range(k)] + ["Kimenetek száma"], [7] + [18] * k + [12])
    for i in range(k):
        szoveg(n2.cell(row=5 + i, column=1), f"{i + 1}.", felkov=True)
        r = 5 + i
        keplet(n2.cell(row=r, column=2 + k), f"=COUNTA(B{r}:{get_column_letter(1 + k)}{r})-IF({get_column_letter(2 + i)}{r}=\"\",0,1)")
    szoveg(n2.cell(row=5 + k, column=1), "Bemenetek", felkov=True)
    for j in range(k):
        col = get_column_letter(2 + j)
        keplet(n2.cell(row=5 + k, column=2 + j), f'=COUNTA({col}5:{col}{4 + k})-IF({col}{5 + j}="",0,1)')
    szoveg(n2.cell(row=7 + k, column=1), "Interfészek összesen", felkov=True)
    keplet(n2.cell(row=7 + k, column=3), f"=SUM({get_column_letter(2 + k)}5:{get_column_letter(2 + k)}{4 + k})")

    el = wb.create_sheet("Elemek")
    cimsor(el, "A DSM elemei")
    sor = [[e["kod"], e["nev"], MODUL[e["kod"]]] for e in D["elemek"]]
    tablazat(el, 4, ["Kód", "Elem neve", "Modul"], [8, 34, 16], sor, bemeneti_oszlopok=(1, 2, 3), uressor=N - len(sor))

    ds = wb.create_sheet("DSM")
    cimsor(ds, "Tervezési struktúramátrix (DSM)", "1 = kapcsolat. Az átló az elem maga. Kölcsönös kapcsolatnál mindkét cellát töltsd ki.")
    kod = [e["kod"] for e in D["elemek"]]
    idx = {c: i for i, c in enumerate(kod)}
    A = [[0] * len(kod) for _ in kod]
    for a, b in D["kapcsolatok"]:
        A[idx[a]][idx[b]] = A[idx[b]][idx[a]] = 1
    R0, C0 = 5, 2
    ds.column_dimensions["A"].width = 9
    for j in range(N):
        ds.column_dimensions[get_column_letter(C0 + j)].width = 5
        c = ds.cell(row=R0 - 1, column=C0 + j)
        keplet(c, f'=IF(Elemek!A{5 + j}="","",Elemek!A{5 + j})')
        c.alignment = kozep
        c.fill, c.font = fej_fill, fej_font
        keplet(ds.cell(row=R0 + j, column=1), f'=IF(Elemek!A{5 + j}="","",Elemek!A{5 + j})')
        ds.cell(row=R0 + j, column=1).fill, ds.cell(row=R0 + j, column=1).font = fej_fill, fej_font
    for i in range(N):
        for j in range(N):
            c = ds.cell(row=R0 + i, column=C0 + j)
            if i == j:
                c.fill = PatternFill("solid", fgColor="1F3F60")
                c.border = keret
            else:
                bemenet(c, (A[i][j] or None) if i < len(kod) and j < len(kod) else None)
                c.alignment = kozep
    # összesítő oszlopok
    oszl = C0 + N
    fejlec(ds, R0 - 1, ["Fokszám"], [9], oszlop=oszl)
    for i in range(N):
        r = R0 + i
        keplet(ds.cell(row=r, column=oszl), f'=IF($A{r}="","",SUM({get_column_letter(C0)}{r}:{get_column_letter(C0 + N - 1)}{r}))')
    # segédrácsok: aszimmetria, modulon belüli, modulok közötti (csak felső háromszög)
    H0 = oszl + 2
    szoveg(ds.cell(row=R0 - 2, column=H0), "Segédszámítás (ne írd felül): aszimmetria | modulon belül | modulok között", felkov=True)
    for g in range(3):
        for i in range(N):
            for j in range(N):
                c = ds.cell(row=R0 + i, column=H0 + g * (N + 1) + j)
                a = f"{get_column_letter(C0 + j)}{R0 + i}"
                b = f"{get_column_letter(C0 + i)}{R0 + j}"
                if g == 0:
                    f = f"=IF(N({a})<>N({b}),1,0)" if i != j else "=0"
                elif j <= i:
                    f = "=0"
                elif g == 1:
                    f = f'=IF(AND(N({a})=1,Elemek!$C${5 + i}<>"",Elemek!$C${5 + i}=Elemek!$C${5 + j}),1,0)'
                else:
                    f = f'=IF(AND(N({a})=1,Elemek!$C${5 + i}<>Elemek!$C${5 + j}),1,0)'
                c.value = f
                c.font = Font(name="Arial", size=8, color="999999")
    def rng(g):
        c1 = get_column_letter(H0 + g * (N + 1))
        c2 = get_column_letter(H0 + g * (N + 1) + N - 1)
        return f"{c1}{R0}:{c2}{R0 + N - 1}"
    rs = R0 + N + 1
    sorok = [("Elemek száma", '=COUNTIF(Elemek!A5:A24,"?*")', None),
             ("Kapcsolatok száma (felső háromszög)", f"=SUM({rng(1)})+SUM({rng(2)})", None),
             ("Aszimmetrikus cellapárok", f"=SUM({rng(0)})/2", None),
             ("Modulokon belüli kapcsolatok", f"=SUM({rng(1)})", None),
             ("Modulok közötti kapcsolatok (modulinterfészek)", f"=SUM({rng(2)})", None),
             ("Modulokon belüli arány", f"=IF(B{rs + 1}=0,\"\",B{rs + 3}/B{rs + 1})", "0%"),
             ("Mátrix sűrűsége", f"=IF(B{rs}<2,\"\",B{rs + 1}/(B{rs}*(B{rs}-1)/2))", "0%")]
    for k_, (t, f, fmt) in enumerate(sorok):
        szoveg(ds.cell(row=rs + k_, column=1), t, felkov=True)
        ds.merge_cells(start_row=rs + k_, start_column=1, end_row=rs + k_, end_column=1)
        keplet(ds.cell(row=rs + k_, column=2), f, fmt)
    ds.column_dimensions["A"].width = 44
    megjegyzes(ds.cell(row=rs + 2, column=2), "Ha nem nulla, valamelyik kapcsolat csak az egyik irányban szerepel. Kölcsönös kapcsolatoknál ez hiba; irányított DSM-nél szándékos lehet.")
    ds.freeze_panes = ds.cell(row=R0, column=C0)
    return mentes(wb, "n2_dsm_sablon.xlsx")
