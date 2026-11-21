"""Pugh-féle összehasonlítás két körrel (eszközlap: Pugh-módszer)."""
import json

from _kozos import *  # noqa: F401,F403

D = json.loads((MAPPA.parents[1] / "_shared" / "adat" / "dontes_kobo.json").read_text(encoding="utf-8"))
JEL = {1: "+", 0: "S", -1: "-"}
NK, NA = 14, 6
MASODIK = {  # 2. kör: datum = A (együttműködő cella)
    "B": ["+", "+", "S", "-", "-", "-", "+", "S"],
    "D": ["+", "+", "+", "-", "-", "-", "-", "S"],
}


def pugh_lap(wb, nev, datum, alternativak, kriteriumok, ertekek):
    ws = wb.create_sheet(nev)
    cimsor(ws, f"Pugh-összehasonlítás – {nev}", "Jelölés: + jobb, S azonos, - rosszabb a vonatkoztatási alapnál. A súly opcionális (üresen hagyva 1).")
    szoveg(ws["A3"], "Vonatkoztatási alap (datum):", felkov=True)
    bemenet(ws["C3"], datum)
    ws.merge_cells("C3:F3")
    fejlec(ws, 5, ["Kritérium", "Súly (opcionális)"] + [""] * NA, [36, 10] + [16] * NA)
    for j in range(NA):
        c = ws.cell(row=5, column=3 + j)
        bemenet(c, alternativak[j] if j < len(alternativak) else None)
        c.alignment = kozep
    for i in range(NK):
        r = 6 + i
        bemenet(ws.cell(row=r, column=1), kriteriumok[i] if i < len(kriteriumok) else None)
        bemenet(ws.cell(row=r, column=2))
        for j in range(NA):
            v = ertekek[j][i] if j < len(ertekek) and i < len(ertekek[j]) else None
            bemenet(ws.cell(row=r, column=3 + j), v)
            ws.cell(row=r, column=3 + j).alignment = kozep
    legordulo(ws, f"C6:{get_column_letter(2 + NA)}{5 + NK}", ["+", "S", "-"])
    re = 6 + NK
    cimkek = ["Pluszok száma", "S száma", "Mínuszok száma", "Előjeles összeg (tájékoztató)", "Súlyozott összeg (tájékoztató)"]
    for k, t in enumerate(cimkek):
        szoveg(ws.cell(row=re + k, column=1), t, felkov=True)
        for j in range(NA):
            col = get_column_letter(3 + j)
            rg = f"{col}6:{col}{5 + NK}"
            if k == 0:
                f = f'=IF({col}$5="","",COUNTIF({rg},"+"))'
            elif k == 1:
                f = f'=IF({col}$5="","",COUNTIF({rg},"S"))'
            elif k == 2:
                f = f'=IF({col}$5="","",COUNTIF({rg},"-"))'
            elif k == 3:
                f = f'=IF({col}$5="","",{col}{re}-{col}{re + 2})'
            else:
                f = (f'=IF({col}$5="","",SUMPRODUCT((($B$6:$B${5 + NK})="")+$B$6:$B${5 + NK},(($A$6:$A${5 + NK})<>"")'
                     f'*(({rg})="+"))-SUMPRODUCT((($B$6:$B${5 + NK})="")+$B$6:$B${5 + NK},(($A$6:$A${5 + NK})<>"")*(({rg})="-")))')
            keplet(ws.cell(row=re + k, column=3 + j), f, felkov=(k == 3))
    megjegyzes(ws.cell(row=re + 3, column=1), "Az összeg csak tájékoztató: a pluszok és mínuszok nem azonos súlyúak. A minta (hol erős, hol gyenge egy koncepció) a fontosabb.")
    szoveg(ws.cell(row=re + 6, column=1), "Megjegyzések, hibrid ötletek:", felkov=True)
    bemenet(ws.cell(row=re + 7, column=1))
    ws.merge_cells(start_row=re + 7, start_column=1, end_row=re + 9, end_column=2 + NA)
    return ws


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Pugh-módszer – sablon", [
        "■ Mire való? Koncepciók gyors, minőségi összehasonlítása egy vonatkoztatási alaphoz (datum), a gyenge koncepciók kiszűrése és hibrid koncepciók ötletének előállítása (Pugh).",
        "1. Válassz vonatkoztatási alapot: a jelenlegi megoldást vagy a legígéretesebbnek tartott koncepciót.",
        "2. Írd be a kritériumokat (a követelményekből és a fontos érdekelt feli szempontokból) és az alternatívákat.",
        "3. Minden cellában döntsd el: jobb (+), azonos (S) vagy rosszabb (-) az alternatíva az alapnál az adott kritérium szerint. A döntés indoklását a csapatban beszéljétek meg.",
        "4. A lap összeszámolja a jeleket. Az összeg csak tájékoztató: a minta a fontosabb. Keresd meg, hogyan javíthatók a legjobb koncepciók gyengeségei más koncepciók erősségeivel.",
        "5. A második körben a legjobb koncepció legyen az új alap, és ismételd meg az összehasonlítást.",
        "■ Példa: a KoboCella négy koncepciója (kézikönyv 10. fejezet). 1. kör: alap a jelenlegi kézi szerelés; 2. kör: alap az együttműködő cella.",
    ])
    p = D["pugh"]
    alt = list(D["alternativak"].items())
    pugh_lap(wb, "1. kör", p["datum"], [f"{k}: {v}" for k, v in alt], p["kriteriumok"],
             [[JEL[x] for x in p["ertekek"][k]] for k, _ in alt])
    pugh_lap(wb, "2. kör", "A: együttműködő cella", [f"{k}: {D['alternativak'][k]}" for k in MASODIK], p["kriteriumok"],
             [MASODIK[k] for k in MASODIK])
    return mentes(wb, "pugh_sablon.xlsx")
