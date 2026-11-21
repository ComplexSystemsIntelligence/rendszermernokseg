"""Súlyozott értékelés (trade study) hasznossági függvényekkel és érzékenységvizsgálattal."""
import json

from _kozos import *  # noqa: F401,F403

D = json.loads((MAPPA.parents[1] / "_shared" / "adat" / "dontes_kobo.json").read_text(encoding="utf-8"))["sulyozott"]
NAMES = json.loads((MAPPA.parents[1] / "_shared" / "adat" / "dontes_kobo.json").read_text(encoding="utf-8"))["alternativak"]
NK, NA = 10, 6


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Súlyozott értékelés (trade study) – sablon", [
        "■ Mire való? Jól definiált alternatívák összehasonlítása több, különböző mértékegységű kritérium szerint, súlyozott hasznossági pontszámmal (Keeney és Raiffa, 1976; Edwards és Barron, 1994).",
        "1. A „Kritériumok” lapon add meg a kritériumokat, a súlyokat (összesen 100) és a lineáris hasznossági függvény két végpontját: a 0 pontot érő („rossz”) és a 10 pontot érő („jó”) szintet. Kisebb-a-jobb kritériumnál a „jó” érték kisebb.",
        "   Szóbeli kritériumnál (például kockázat) a típus legyen „szóbeli”; a pontszámot a „Skála” lap adja.",
        "2. Az „Értékelés” lapon írd be az alternatívák becsült vagy mért értékeit. A lap kiszámolja a 0–10 pontszámokat (a végpontokon túl levágva), a súlyozott összpontszámot és a rangsort.",
        "3. A súlyokat lehetőleg a döntéshozó rögzítse a pontozás előtt, az értékelőktől függetlenül.",
        "4. Az „Érzékenység” lapon válassz egy kritériumot: a lap a súlyát 0 és 50 között változtatja (a többit arányosan), és megmutatja, hol fordul meg a rangsor.",
        "5. Minőségi pontszámoknál a fél skálalépésnél kisebb különbséget érdemes egyenértékű eredménynek tekinteni. Szoros eredménynél gyűjts több adatot, vagy mutasd be mindkét alternatívát.",
        "■ Példa: a KoboCella három koncepciója (kézikönyv 10. fejezet).",
    ])
    sk = wb.create_sheet("Skála")
    cimsor(sk, "Szóbeli skála", "Operatív definíció: írd le, mit jelent az egyes szint (például valószínűség vagy tapasztalat).")
    tablazat(sk, 4, ["Szint", "Pontszám (0–10)", "Operatív definíció"], [14, 14, 70],
             [["alacsony", 9, "a technológia a cégnél vagy közvetlen referenciánál bizonyított"],
              ["közepes", 6, "a technológia az iparágban bizonyított, a cégnél új"],
              ["magas", 2, "a megoldás több új elemet egyszerre igényel, nincs közvetlen referencia"]],
             bemeneti_oszlopok=(1, 2, 3), uressor=4)
    kr = wb.create_sheet("Kritériumok")
    cimsor(kr, "Kritériumok és hasznossági függvények")
    sor = []
    for k in D["kriteriumok"]:
        if "skala" in k:
            sor.append([k["kod"], k["nev"], k["egyseg"], k["suly"], "szóbeli", None, None])
        else:
            sor.append([k["kod"], k["nev"], k["egyseg"], k["suly"], "lineáris", k["rossz"], k["jo"]])
    u = tablazat(kr, 4, ["Kód", "Kritérium", "Mértékegység", "Súly", "Típus", "„Rossz” szint (0 pont)", "„Jó” szint (10 pont)"],
                 [7, 32, 13, 9, 12, 16, 16], sor, bemeneti_oszlopok=range(1, 8), uressor=NK - len(sor))
    legordulo(kr, f"E5:E{u}", ["lineáris", "szóbeli"])
    szoveg(kr.cell(row=u + 2, column=2), "Súlyok összege (100 kell legyen)", felkov=True)
    keplet(kr.cell(row=u + 2, column=4), f"=SUM(D5:D{u})", felkov=True)
    keplet(kr.cell(row=u + 2, column=5), f'=IF(D{u + 2}=100,"rendben","javítsd!")')

    ev = wb.create_sheet("Értékelés")
    cimsor(ev, "Értékelés", "Felső blokk: a kritériumok szerinti értékek (bemenet). Alsó blokk: 0–10 pontszámok és súlyozott összpontszám (képlet).")
    alts = D["alternativak"]
    fejlec(ev, 4, ["Kód", "Kritérium"] + [""] * NA, [7, 32] + [16] * NA)
    for j in range(NA):
        c = ev.cell(row=4, column=3 + j)
        bemenet(c, f"{alts[j]}: {NAMES[alts[j]]}" if j < len(alts) else None)
        c.alignment = kozep
    for i in range(NK):
        r = 5 + i
        keplet(ev.cell(row=r, column=1), f'=IF(Kritériumok!A{5 + i}="","",Kritériumok!A{5 + i})')
        keplet(ev.cell(row=r, column=2), f'=IF(Kritériumok!B{5 + i}="","",Kritériumok!B{5 + i})')
        k = D["kriteriumok"][i] if i < len(D["kriteriumok"]) else None
        for j in range(NA):
            v = k["ertekek"][j] if k and j < len(k["ertekek"]) else None
            bemenet(ev.cell(row=r, column=3 + j), v)
            ev.cell(row=r, column=3 + j).alignment = kozep
    P0 = 7 + NK
    fejlec(ev, P0 - 1, ["Kód", "Pontszám (0–10)"] + [""] * NA)
    for j in range(NA):
        col = get_column_letter(3 + j)
        keplet(ev.cell(row=P0 - 1, column=3 + j), f'=IF({col}4="","",{col}4)')
        ev.cell(row=P0 - 1, column=3 + j).fill, ev.cell(row=P0 - 1, column=3 + j).font = fej_fill, fej_font
    for i in range(NK):
        r = P0 + i
        kri = 5 + i
        keplet(ev.cell(row=r, column=1), f"=A{5 + i}")
        keplet(ev.cell(row=r, column=2), f"=B{5 + i}")
        for j in range(NA):
            col = get_column_letter(3 + j)
            x = f"{col}{5 + i}"
            f = (f'=IF(OR(${col}$4="",{x}="",Kritériumok!$B${kri}=""),"",IF(Kritériumok!$E${kri}="szóbeli",'
                 f'IFERROR(INDEX(Skála!$B$5:$B$11,MATCH({x},Skála!$A$5:$A$11,0)),""),'
                 f'ROUND(MAX(0,MIN(10,10*({x}-Kritériumok!$F${kri})/(Kritériumok!$G${kri}-Kritériumok!$F${kri}))),1)))')
            keplet(ev.cell(row=r, column=3 + j), f, "0.0")
    rt = P0 + NK
    szoveg(ev.cell(row=rt, column=2), "Súlyozott összpontszám (0–10)", felkov=True)
    szoveg(ev.cell(row=rt + 1, column=2), "Rang", felkov=True)
    szoveg(ev.cell(row=rt + 2, column=2), "Különbség az elsőtől", felkov=True)
    for j in range(NA):
        col = get_column_letter(3 + j)
        keplet(ev.cell(row=rt, column=3 + j),
               f'=IF({col}$4="","",SUMPRODUCT(Kritériumok!$D$5:$D${4 + NK},{col}{P0}:{col}{P0 + NK - 1})/SUM(Kritériumok!$D$5:$D${4 + NK}))', "0.00", True)
        keplet(ev.cell(row=rt + 1, column=3 + j), f'=IF({col}$4="","",RANK({col}{rt},$C${rt}:${get_column_letter(2 + NA)}${rt}))')
        keplet(ev.cell(row=rt + 2, column=3 + j), f'=IF({col}$4="","",MAX($C${rt}:${get_column_letter(2 + NA)}${rt})-{col}{rt})', "0.00")
    megjegyzes(ev.cell(row=rt + 2, column=2), "Ökölszabály: a fél skálalépésnél (itt 0,5 pont) kisebb különbség egyenértékű eredménynek tekinthető; döntés előtt érzékenységvizsgálat kell.")

    er = wb.create_sheet("Érzékenység")
    cimsor(er, "Egytényezős érzékenységvizsgálat", "A választott kritérium súlyát 0 és 50 között változtatjuk, a többi súlyt arányosan módosítjuk.")
    szoveg(er["A3"], "Vizsgált kritérium kódja:", felkov=True)
    bemenet(er["C3"], "K5")
    szoveg(er["D3"], "Alapsúly:", felkov=True)
    keplet(er["E3"], "=INDEX(Kritériumok!$D$5:$D$14,MATCH($C$3,Kritériumok!$A$5:$A$14,0))")
    fejlec(er, 5, ["A kritérium súlya"] + [""] * NA, [18] + [16] * NA)
    for j in range(NA):
        col = get_column_letter(3 + j)
        keplet(er.cell(row=5, column=2 + j), f'=IF(Értékelés!{col}4="","",Értékelés!{col}4)')
        er.cell(row=5, column=2 + j).fill, er.cell(row=5, column=2 + j).font = fej_fill, fej_font
    W = f"Kritériumok!$D$5:$D${4 + NK}"
    for i, w in enumerate(range(0, 51, 5)):
        r = 6 + i
        bemenet(er.cell(row=r, column=1), w)
        for j in range(NA):
            col = get_column_letter(3 + j)
            Ucol = f"Értékelés!{col}${P0}:{col}${P0 + NK - 1}"
            uk = f"INDEX({Ucol},MATCH($C$3,Kritériumok!$A$5:$A${4 + NK},0))"
            f = (f'=IF(Értékelés!{col}$4="","",($A{r}*{uk}+(SUM({W})-$A{r})/(SUM({W})-$E$3)*(SUMPRODUCT({W},{Ucol})-$E$3*{uk}))/SUM({W}))')
            keplet(er.cell(row=r, column=2 + j), f, "0.00")
    ch = LineChart()
    for j in range(len(alts)):
        ch.add_data(Reference(er, min_col=2 + j, min_row=5, max_row=16), titles_from_data=True)
    ch.set_categories(Reference(er, min_col=1, min_row=6, max_row=16))
    diagram_kozos(ch, "Súlyozott összpontszám a kritérium súlyának függvényében", "a vizsgált kritérium súlya", "összpontszám", 18, 9)
    er.add_chart(ch, "A19")
    return mentes(wb, "trade_study_sablon.xlsx")
