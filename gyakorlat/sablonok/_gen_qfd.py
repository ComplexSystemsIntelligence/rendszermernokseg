"""Minőségház (QFD) sablon a kézikönyv VárosiBringa-példájával (_shared/adat/qfd_bringa.json)."""
import json

from _kozos import *  # noqa: F401,F403
from openpyxl.formatting.rule import CellIsRule

ADAT = json.loads((MAPPA.parents[1] / "_shared" / "adat" / "qfd_bringa.json").read_text(encoding="utf-8"))
NE, NM = 10, 10          # sablonkapacitás: elvárások és jellemzők száma
TETO = ["++", "+", "-", "--"]


def haz_lap(wb, nev, adat):
    ws = wb.create_sheet(nev)
    cimsor(ws, "Minőségház (House of Quality)", "Kapcsolat: 9 erős, 3 közepes, 1 gyenge, üres = nincs. Vevői értékelés: 1–5.")
    # oszlopok: A kód, B elvárás, C fontosság, D..M jellemzők (10), N saját, O A, P B, Q javítási arány
    ws.column_dimensions["A"].width = 7
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 10
    for j in range(NM):
        ws.column_dimensions[get_column_letter(4 + j)].width = 11
    for k, c in enumerate(["N", "O", "P", "Q"]):
        ws.column_dimensions[c].width = 10 if k < 3 else 12
    # fejlécsorok: 4 kód, 5 név, 6 egység, 7 irány, 8 célérték
    for r, cim in zip(range(4, 9), ["Jellemző kódja", "Műszaki jellemző", "Mértékegység", "Irány (max/min)", "Célérték"]):
        c = ws.cell(row=r, column=3, value=cim)
        c.font, c.fill, c.alignment, c.border = fej_font, fej_fill, kozep, keret
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2) if False else None
    jell = adat["jellemzok"] if adat else []
    for j in range(NM):
        t = jell[j] if j < len(jell) else {}
        col = 4 + j
        for r, kul in zip(range(4, 9), ["kod", "nev", "egyseg", "irany", "cel"]):
            bemenet(ws.cell(row=r, column=col), t.get(kul))
            ws.cell(row=r, column=col).alignment = kozep
    ws.row_dimensions[5].height = 60
    legordulo(ws, f"D7:{get_column_letter(3 + NM)}7", ["max", "min"])
    fejlec(ws, 9, ["Kód", "Vevői elvárás", "Fontosság (1–5)"] + [""] * NM + ["Saját", "A versenytárs", "B versenytárs", "Lemaradás a legjobbtól"])
    ws.row_dimensions[9].height = 30
    elv = adat["elvarasok"] if adat else []
    R = adat["kapcsolat"] if adat else []
    for i in range(NE):
        r = 10 + i
        e = elv[i] if i < len(elv) else {}
        bemenet(ws.cell(row=r, column=1), e.get("kod"))
        bemenet(ws.cell(row=r, column=2), e.get("nev"))
        bemenet(ws.cell(row=r, column=3), e.get("fontossag"))
        for j in range(NM):
            v = R[i][j] if (i < len(R) and j < len(R[i]) and R[i][j]) else None
            c = bemenet(ws.cell(row=r, column=4 + j), v)
            c.alignment = kozep
        for k, kul in enumerate(["sajat", "A", "B"]):
            bemenet(ws.cell(row=r, column=14 + k), e.get(kul)).alignment = kozep
        keplet(ws.cell(row=r, column=17), f'=IF(N{r}="","",MAX(N{r}:P{r})-N{r})')
    dv = DataValidation(type="list", formula1='"0,1,3,9"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"D10:{get_column_letter(3 + NM)}{9 + NE}")
    # alsó sorok
    fr = 10 + NE
    for k, cim in enumerate(["Abszolút fontosság", "Relatív fontosság", "Rangsor"]):
        c = ws.cell(row=fr + k, column=3, value=cim)
        c.font, c.fill, c.border, c.alignment = fej_font, fej_fill, keret, kozep
    for j in range(NM):
        col = get_column_letter(4 + j)
        keplet(ws.cell(row=fr, column=4 + j), f'=IF({col}$4="","",SUMPRODUCT($C$10:$C${fr - 1},{col}10:{col}{fr - 1}))', felkov=True)
        keplet(ws.cell(row=fr + 1, column=4 + j), f'=IF({col}{fr}="","",{col}{fr}/SUM($D${fr}:${get_column_letter(3 + NM)}${fr}))', "0.0%")
        keplet(ws.cell(row=fr + 2, column=4 + j), f'=IF({col}{fr}="","",RANK({col}{fr},$D${fr}:${get_column_letter(3 + NM)}${fr}))')
    ws.conditional_formatting.add(f"D10:{get_column_letter(3 + NM)}{9 + NE}",
                                  CellIsRule(operator="equal", formula=["9"], fill=PatternFill("solid", fgColor="A9C4DE")))
    ws.freeze_panes = "D10"
    # diagram
    ch = BarChart()
    ch.add_data(Reference(ws, min_col=4, max_col=3 + max(len(jell), 1), min_row=fr + 1), from_rows=True, titles_from_data=False)
    ch.set_categories(Reference(ws, min_col=4, max_col=3 + max(len(jell), 1), min_row=4))
    diagram_kozos(ch, "A műszaki jellemzők relatív fontossága", None, None, 18, 8)
    ch.legend = None
    ws.add_chart(ch, f"B{fr + 5}")
    return ws


def teto_lap(wb, nev, adat):
    ws = wb.create_sheet(nev)
    cimsor(ws, "Tető: a műszaki jellemzők kölcsönhatása",
           "A főátló feletti cellákba: ++ erősen támogatja, + támogatja, - gyengíti, -- erősen gyengíti egymást.")
    jell = adat["jellemzok"] if adat else []
    kodok = [t["kod"] for t in jell] + [None] * (NM - len(jell))
    fejlec(ws, 4, [""] + [k or "" for k in kodok], [8] + [8] * NM)
    idx = {t["kod"]: k for k, t in enumerate(jell)}
    teto = {}
    for t in (adat or {}).get("tetokapcsolat", []):
        a, b = sorted((idx[t["a"]], idx[t["b"]]))
        teto[(a, b)] = "--" if t["jel"] == "--" else t["jel"]
    for i in range(NM):
        c = ws.cell(row=5 + i, column=1, value=kodok[i])
        c.font, c.fill, c.border, c.alignment = fej_font, fej_fill, keret, kozep
        for j in range(NM):
            cell = ws.cell(row=5 + i, column=2 + j)
            if j > i:
                bemenet(cell, teto.get((i, j))).alignment = kozep
            else:
                cell.fill = PatternFill("solid", fgColor="D9D9D9")
                cell.border = keret
    legordulo(ws, f"B5:{get_column_letter(1 + NM)}{4 + NM}", TETO)
    megjegyzes(ws["A4"], "A jellemzők kódjai a „Minőségház” lap 4. sorából; a sorrendnek egyeznie kell.")
    return ws


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Minőségház (QFD) – sablon", [
        "■ Mire való? A vevői elvárások lefordítása mérhető műszaki jellemzőkre, ezek fontossági sorrendjének és célértékeinek meghatározása.",
        "1. A „Minőségház” lap 4–8. sorában add meg a műszaki jellemzőket: kód, név, mértékegység, irány (max: nagyobb a jobb, min: kisebb a jobb), célérték.",
        "2. A 10. sortól írd be a vevői elvárásokat és fontosságukat (1–5), majd töltsd ki a kapcsolati mátrixot (9, 3, 1 vagy üres).",
        "3. A jobb oldalon a vevők értékelése a saját és két versenytárs megoldásról (1–5); a „Lemaradás” oszlop mutatja, hol vagyunk elmaradva a legjobbtól.",
        "4. Az alsó sorok automatikusan számolják a műszaki jellemzők abszolút és relatív fontosságát és rangsorát; a diagram a relatív fontosságot mutatja.",
        "5. A „Tető” lapon rögzítsd a műszaki jellemzők kölcsönhatását. A negatív kapcsolatok kompromisszumot vagy innovatív megoldást igényelnek (TRIZ).",
        "■ Példa: a „Példa –” lapok a kézikönyv VárosiBringa-minőségházát tartalmazzák (7. fejezet).",
    ])
    haz_lap(wb, "Minőségház", None)
    teto_lap(wb, "Tető", None)
    haz_lap(wb, "Példa – minőségház", ADAT)
    teto_lap(wb, "Példa – tető", ADAT)
    return mentes(wb, "qfd_sablon.xlsx")


if __name__ == "__main__":
    keszit()
