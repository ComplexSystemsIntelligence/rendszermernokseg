"""MOE–MOP–TPM hierarchia és TPM-követés (eszközlap: MOE, MOP, TPM)."""
from _kozos import *  # noqa: F401,F403

HIER = [
    ("MOE-1", "A vevői igény teljesítése elfogadható minőségben", "MOP-1", "Ciklusidő a referencia-motortípusra", "s", "≤ 75", "≤ 70", "betanult operátor, folyamatos üzem", "igen", "R-01"),
    ("MOE-1", "", "MOP-2", "Havi rendelkezésre állás", "%", "≥ 95", "≥ 97", "tervezett leállások nélkül", "nem", "R-02"),
    ("MOE-1", "", "MOP-3", "Első átfutásra jó darabok aránya", "%", "≥ 99,5", "≥ 99,8", "nyomatékellenőrzéssel", "igen", "R-03, R-07"),
    ("MOE-2", "Az operátorok ergonómiai terhelésének csökkentése", "MOP-4", "Legnagyobb törzshajlítás egy ciklusban", "fok", "≤ 20", "≤ 15", "minden testmagassági csoportra", "nem", "R-05"),
    ("MOE-2", "", "MOP-5", "Kézzel tartott szerszám tömege", "kg", "0", "0", "normál üzemben", "nem", "R-06"),
]
TPM = [  # mérföldkő, tervezett, alsó, felső, becsült/mért
    ("SRR", 83.0, 80.0, 86.0, 84.0),
    ("PDR", 79.5, 77.0, 82.0, 81.5),
    ("CDR", 76.8, 74.5, 79.0, 78.2),
    ("FAT", 74.5, 72.5, 76.5, 77.4),
    ("SAT", 73.8, 72.0, 75.5, None),
    ("TRR", 73.2, 71.5, 75.0, None),
    ("ORR", 73.2, 71.5, 75.0, None),
]


def tpm_lap(wb, nev, adatok, kuszob=75.0, cel=70.0, irany="min"):
    ws = wb.create_sheet(nev)
    cimsor(ws, "TPM-követés", "Egy TPM lapja: tervezett lefutás tűrésmezővel, becsült vagy mért értékek, küszöb és célérték.")
    szoveg(ws["A3"], "TPM:", felkov=True)
    bemenet(ws["B3"], "MOP-1 ciklusidő [s]")
    szoveg(ws["D3"], "Küszöb (követelmény):", felkov=True)
    bemenet(ws["E3"], kuszob)
    szoveg(ws["F3"], "Célérték:", felkov=True)
    bemenet(ws["G3"], cel)
    szoveg(ws["H3"], "Irány (min/max):", felkov=True)
    bemenet(ws["I3"], irany)
    legordulo(ws, "I3", ["min", "max"])
    fej = ["Mérföldkő", "Tervezett érték", "Tűrés alsó határa", "Tűrés felső határa", "Becsült / mért érték",
           "Eltérés a tervtől", "Állapot", "Tartalék a küszöbig", "Küszöb (diagramhoz)", "Célérték (diagramhoz)"]
    kepl = {
        6: lambda r: f'=IF(E{r}="","",E{r}-B{r})',
        7: lambda r: f'=IF(E{r}="","",IF(AND(E{r}>=C{r},E{r}<=D{r}),"tűrésen belül","tűrésen kívül – beavatkozás"))',
        8: lambda r: f'=IF(E{r}="","",IF($I$3="min",$E$3-E{r},E{r}-$E$3))',
        9: lambda r: "=$E$3",
        10: lambda r: "=$G$3",
    }
    u = tablazat(ws, 5, fej, [12, 13, 13, 13, 14, 12, 26, 14, 12, 12], adatok, bemeneti_oszlopok=range(1, 6),
                 kepletek=kepl, uressor=3, formatumok={2: "0.0", 3: "0.0", 4: "0.0", 5: "0.0", 6: "+0.0;-0.0;0.0", 8: "+0.0;-0.0;0.0"})
    megjegyzes(ws["H5"], "Pozitív: a küszöb teljesül, ennyi a tartalék. Negatív: a küszöb nem teljesül.")
    ch = LineChart()
    for col in (2, 3, 4, 5, 9, 10):
        ch.add_data(Reference(ws, min_col=col, min_row=5, max_row=u - 3), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=6, max_row=u - 3))
    diagram_kozos(ch, "TPM-követés", "mérföldkő", "érték", 20, 10)
    stil = [("4F7FAD", "dash"), ("A9C4DE", "sysDot"), ("A9C4DE", "sysDot"), ("E07B39", None), ("B83A3A", None), ("285780", "dot")]
    for s, (szin, dash) in zip(ch.series, stil):
        s.graphicalProperties.line.solidFill = szin
        s.graphicalProperties.line.width = 28000 if szin == "E07B39" else 19000
        if dash:
            s.graphicalProperties.line.dashStyle = dash
        s.smooth = False
    ch.series[3].marker.symbol = "circle"
    ws.add_chart(ch, f"A{u + 3}")
    return ws


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "MOE, MOP, TPM – sablon", [
        "■ Mire való? A rendszer sikerének mérőszámait (MOE) teljesítménymérőszámokra (MOP) bontani, és a kritikus jellemzőket (TPM) a fejlesztés során nyomon követni.",
        "1. A „Hierarchia” lapon minden MOE alá legalább két MOP-ot írj. A MOP-hoz mértékegység, küszöb (követelmény), célérték és feltételek tartoznak (Kossiakoff és mtsai: mérőszám + egység + feltételek).",
        "2. Jelöld meg, mely MOP-ok kritikusak (TPM = igen). Ezeket kell rendszeresen becsülni vagy mérni.",
        "3. A „TPM-követés” lapon add meg a küszöböt, a célértéket, az irányt, és mérföldkövenként a tervezett lefutást a tűrésmezővel. A felülvizsgálatokon írd be a becsült vagy mért értéket.",
        "4. Az „Állapot” oszlop jelzi, ha az érték kilép a tűrésmezőből: ilyenkor beavatkozás kell, még ha a végső küszöb elvileg teljesíthető is.",
        "■ Példa: a KoboCella MOE-MOP hierarchiája és ciklusidejének TPM-követése (kézikönyv 6. fejezet).",
    ])
    ws = wb.create_sheet("Hierarchia")
    cimsor(ws, "MOE–MOP hierarchia")
    tablazat(ws, 4, ["MOE azonosító", "MOE (az érdekelt fél nézőpontjából)", "MOP azonosító", "MOP (műszaki jellemző)",
                     "Mértékegység", "Küszöb", "Célérték", "Feltételek", "TPM?", "Kapcsolódó követelmény"],
             [11, 36, 11, 34, 11, 10, 10, 30, 8, 16], HIER, bemeneti_oszlopok=range(1, 11), uressor=20)
    legordulo(ws, "I5:I30", ["igen", "nem"])
    tpm_lap(wb, "TPM-követés", TPM)
    return mentes(wb, "moe_mop_tpm_sablon.xlsx")


if __name__ == "__main__":
    keszit()
