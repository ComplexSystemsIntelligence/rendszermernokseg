"""Eseménynapló-sablon és adatminőség-ellenőrzés a folyamatbányászathoz (eszközlap: Folyamatbányászat alapjai)."""
from openpyxl.formatting.rule import FormulaRule

from _esemenynaplo_adat import ESETEK, MODELL_KOVETESEK, NAPLO
from _kozos import *  # noqa: F401,F403

TEV = ["Rendelés rögzítése", "Visszaigazolás", "Ütemezés", "Rendelés átsorolása", "Anyagkiadás", "Megmunkálás",
       "Mérés", "Utómunka", "Csomagolás", "Kiszállítás"]
NT, NURES, NEUR = 15, 500, 100
DT = "yyyy.mm.dd hh:mm"
PIROS = PatternFill("solid", fgColor="F6D5D5")


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Eseménynapló és folyamatbányászat – sablon", [
        "■ Mire való? Egy informatikai rendszer eseménynaplójának előkészítése és első elemzése folyamatbányászathoz: adatminőség, "
        "tevékenységek gyakorisága és időtartama, közvetlen követések (közvetlen követési mátrix), eltérések a folyamatmodelltől, esetenkénti átfutás.",
        "■ Napló: egy sor egy esemény. Kötelező: esetazonosító, tevékenység, kezdés (és lehetőleg befejezés) időbélyege; ajánlott: erőforrás. "
        "A sorokat esetenként, azon belül időrendben rendezd (a sablon a szomszédos sorokból képzi a közvetlen követéseket).",
        "■ Tevékenységek: az egységes tevékenységnevek listája (legfeljebb 15). A naplóban ettől eltérő név adatminőségi hibának számít.",
        "■ Modell: a folyamatmodell szerint megengedett közvetlen követések (honnan → hová). A naplóban ettől eltérő követés eltérés.",
        "■ Követések: a közvetlen követési mátrix; pirosak a modellben nem szereplő, de a naplóban előforduló követések.",
        "■ Esetek: esetenként a rendelés dátuma és a határidő (bemenet), valamint az átfutás, a késés, az átsorolás és a modelltől való eltérés (számított).",
        "■ Összesítés: adatminőség és a fő mutatók.",
        "A kitöltött példa a ForgácsTech MES-ének szimulált eseménynaplója az első három hónapból: 300 rendelés (kézikönyv 20. és 25. fejezet).",
        "Források: van der Aalst: Process Mining (2016); Dumas és mtsai: Fundamentals of Business Process Management (2018).",
    ])

    # ---- Tevékenységek
    wt = wb.create_sheet("Tevékenységek")
    cimsor(wt, "Tevékenységek", "Egységes tevékenységnevek; a darabszámok és időtartamok a naplóból.")

    # ---- Modell
    wm = wb.create_sheet("Modell")
    cimsor(wm, "A modell szerint megengedett közvetlen követések", "A jövőbeli BPMN-modellből (kézikönyv 20. fejezet).")
    sorrend = {t: i for i, t in enumerate(TEV)}
    modell = sorted(MODELL_KOVETESEK, key=lambda p: (sorrend[p[0]], sorrend[p[1]]))
    m_ut = tablazat(wm, 4, ["Honnan", "Hová"], [26, 26], [list(p) for p in modell] + [["Kiszállítás", "(vége)"]],
                    bemeneti_oszlopok=(1, 2), uressor=20)
    MA, MB = f"'Modell'!$A$5:$A${m_ut}", f"'Modell'!$B$5:$B${m_ut}"

    # ---- Napló
    wn = wb.create_sheet("Napló")
    cimsor(wn, "Eseménynapló", "Esetenként, azon belül időrendben rendezve.")
    fej = ["Eset", "Tevékenység", "Kezdés", "Befejezés", "Erőforrás", "Időtartam [óra]", "Új eset", "Ismert tevékenység",
           "Időrend hiba", "Következő tevékenység", "A modellben?", "Első az esetben"]
    TL = f"'Tevékenységek'!$A$5:$A${4 + NT}"

    def kov(r):
        return f'=IF(A{r}="","",IF(A{r + 1}=A{r},B{r + 1},"(vége)"))'

    ut = tablazat(wn, 4, fej, [9, 22, 17, 17, 14, 11, 8, 11, 9, 22, 10, 10], [list(x) for x in NAPLO],
                  bemeneti_oszlopok=(1, 2, 3, 4, 5),
                  kepletek={6: lambda r: f'=IF(OR(C{r}="",D{r}=""),"",(D{r}-C{r})*24)',
                            7: lambda r: f'=IF(A{r}="","",IF(A{r}<>A{r - 1},1,0))' if r > 5 else f'=IF(A{r}="","",1)',
                            8: lambda r: f'=IF(B{r}="","",IF(COUNTIF({TL},B{r})>0,1,0))',
                            9: lambda r: f'=IF(OR(C{r}="",D{r}=""),"",IF(D{r}<C{r},1,0))',
                            10: kov,
                            11: lambda r: f'=IF(A{r}="","",IF(COUNTIFS({MA},B{r},{MB},J{r})>0,1,0))',
                            12: lambda r: f'=IF(A{r}="","",IF(COUNTIFS($A$5:A{r},A{r},$B$5:B{r},B{r})=1,1,0))'},
                  uressor=NURES, formatumok={3: DT, 4: DT, 6: "0.0"})
    wn.conditional_formatting.add(f"K5:K{ut}", FormulaRule(formula=["K5=0"], fill=PIROS))
    wn.conditional_formatting.add(f"H5:H{ut}", FormulaRule(formula=["H5=0"], fill=PIROS))
    wn.freeze_panes = "A5"
    N_UT = ut
    NA, NB_, NC, ND, NF, NJ, NK, NL = (f"'Napló'!${c}$5:${c}${N_UT}" for c in "ABCDFJKL")

    # Tevékenységek lap tartalma (a Napló után, mert rá hivatkozik)
    tablazat(wt, 4, ["Tevékenység", "Események", "Átlagos időtartam [óra]", "Esetek aránya, amelyekben előfordul"],
             [26, 11, 14, 18], [[t] for t in TEV], bemeneti_oszlopok=(1,),
             kepletek={2: lambda r: f'=IF(A{r}="","",COUNTIF({NB_},A{r}))',
                       3: lambda r: f'=IF(OR(A{r}="",N(B{r})=0),"",AVERAGEIF({NB_},A{r},{NF}))',
                       4: lambda r: f"=IF(A{r}=\"\",\"\",IF('Összesítés'!$B$5=0,\"\",SUMIFS({NL},{NB_},A{r})/'Összesítés'!$B$5))"},
             uressor=NT - len(TEV), formatumok={2: "0", 3: "0.0", 4: "0%"})

    # ---- Követések (közvetlen követési mátrix)
    wk = wb.create_sheet("Követések")
    cimsor(wk, "Közvetlen követési mátrix", "Sor: a tevékenység, oszlop: a közvetlenül utána következő. Piros: a modellben nem szerepel.")
    wk.column_dimensions["A"].width = 24
    oszl = TEV + ["(vége)"]
    for j, t in enumerate(oszl):
        c = wk.cell(row=4, column=2 + j, value=t)
        c.font, c.fill, c.alignment, c.border = fej_font, fej_fill, kozep, keret
        wk.column_dimensions[get_column_letter(2 + j)].width = 11
    wk.row_dimensions[4].height = 46
    for i, t in enumerate(TEV):
        r = 5 + i
        c = wk.cell(row=r, column=1, value=t)
        c.font, c.fill, c.border = fej_font, fej_fill, keret
        for j in range(len(oszl)):
            cl = get_column_letter(2 + j)
            keplet(wk.cell(row=r, column=2 + j), f"=COUNTIFS({NB_},$A{r},{NJ},{cl}$4)", "0;;")
    zona = f"B5:{get_column_letter(1 + len(oszl))}{4 + len(TEV)}"
    wk.conditional_formatting.add(zona, FormulaRule(formula=[f"AND(B5>0,COUNTIFS({MA},$A5,{MB},B$4)=0)"], fill=PIROS))
    wk.conditional_formatting.add(zona, FormulaRule(formula=["B5>0"], fill=PatternFill("solid", fgColor="E6EEF6")))

    # ---- Esetek
    we = wb.create_sheet("Esetek")
    cimsor(we, "Esetek", "A rendelés dátuma és a határidő bemenet; a többi a naplóból számolódik.")
    fej = ["Eset", "Rendelés", "Határidő", "Gép", "Első esemény", "Utolsó esemény", "Átfutás [nap]", "Késve?",
           "Átsorolva?", "Eltérés a modelltől?", "Események"]
    ute = tablazat(we, 4, fej, [9, 17, 17, 7, 17, 17, 11, 8, 10, 12, 10], [list(x) for x in ESETEK],
                   bemeneti_oszlopok=(1, 2, 3, 4),
                   kepletek={5: lambda r: f'=IF(A{r}="","",_xlfn.MINIFS({NC},{NA},A{r}))',
                             6: lambda r: f'=IF(A{r}="","",_xlfn.MAXIFS({ND},{NA},A{r}))',
                             7: lambda r: f'=IF(OR(A{r}="",B{r}=""),"",F{r}-B{r})',
                             8: lambda r: f'=IF(OR(A{r}="",C{r}=""),"",IF(F{r}>C{r},1,0))',
                             9: lambda r: f'=IF(A{r}="","",IF(COUNTIFS({NA},A{r},{NB_},"Rendelés átsorolása")>0,1,0))',
                             10: lambda r: f'=IF(A{r}="","",IF(COUNTIFS({NA},A{r},{NK},0)>0,1,0))',
                             11: lambda r: f'=IF(A{r}="","",COUNTIF({NA},A{r}))'},
                   uressor=NEUR, formatumok={2: DT, 3: DT, 5: DT, 6: DT, 7: "0.0"})
    we.conditional_formatting.add(f"H5:H{ute}", FormulaRule(formula=["H5=1"], fill=PIROS))
    we.freeze_panes = "B5"
    EA, EG, EH, EI, EJ = (f"'Esetek'!${c}$5:${c}${ute}" for c in "AGHIJ")

    # ---- Összesítés
    wo = wb.create_sheet("Összesítés")
    cimsor(wo, "Összesítés")
    wo.column_dimensions["A"].width = 54
    wo.column_dimensions["B"].width = 14
    fejlec(wo, 4, ["Mutató", "Érték"])
    mut = [
        ("Esetek száma (a naplóban)", f"=SUM('Napló'!G5:G{N_UT})", "0"),
        ("Események száma", f"=COUNTA({NA})", "0"),
        ("Események esetenként (átlag)", "=IF(B5=0,\"\",B6/B5)", "0.0"),
        ("Ismeretlen tevékenységnevű események", f"=COUNTIF('Napló'!H5:H{N_UT},0)", "0"),
        ("Hiányzó időbélyeg", f"=COUNTA({NA})-COUNT({NC})+COUNTA({NA})-COUNT({ND})", "0"),
        ("Időrend hiba (befejezés a kezdés előtt)", f"=SUM('Napló'!I5:I{N_UT})", "0"),
        ("Az Esetek lapon hiányzó esetek", f"=B5-COUNTA({EA})", "0"),
        ("Határidőre teljesült esetek aránya", f'=IF(COUNT({EH})=0,"",1-SUM({EH})/COUNT({EH}))', "0.0%"),
        ("Átlagos átfutás [nap]", f"=AVERAGE({EG})", "0.0"),
        ("Átsorolt esetek aránya", f'=IF(COUNT({EI})=0,"",SUM({EI})/COUNT({EI}))', "0.0%"),
        ("Átlagos átfutás, átsorolt esetek [nap]", f'=IF(SUM({EI})=0,"",AVERAGEIF({EI},1,{EG}))', "0.0"),
        ("Átlagos átfutás, nem átsorolt esetek [nap]", f'=IF(COUNTIF({EI},0)=0,"",AVERAGEIF({EI},0,{EG}))', "0.0"),
        ("A modelltől eltérő esetek aránya", f'=IF(COUNT({EJ})=0,"",SUM({EJ})/COUNT({EJ}))', "0.0%"),
        ("A modellben nem szereplő közvetlen követések száma", f"=COUNTIF({NK},0)", "0"),
    ]
    for i, (n, f, fm) in enumerate(mut):
        szoveg(wo.cell(row=5 + i, column=1), n)
        keplet(wo.cell(row=5 + i, column=2), f, fm, i in (7, 12))
    wo.conditional_formatting.add("B8:B11", FormulaRule(formula=["B8>0"], fill=PIROS))
    szoveg(wo.cell(row=21, column=1), "Olvasat: az adatminőségi hibákat (ismeretlen nevek, hiányzó vagy rossz sorrendű időbélyegek) az "
                                     "elemzés előtt javítani kell. A modelltől eltérő esetek nem feltétlenül hibásak: a napló a valós "
                                     "működést mutatja, és a modellt is felül kell vizsgálni.")
    wo.merge_cells("A21:F21")
    wo.row_dimensions[21].height = 45
    rend = ["Útmutató", "Napló", "Esetek", "Tevékenységek", "Modell", "Követések", "Összesítés"]
    wb._sheets = [wb[n] for n in rend]
    return mentes(wb, "folyamatbanyaszat_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
