"""Közös kockázati skála a kockázati mátrix és a PHA sablonhoz (kézikönyv 14. fejezet)."""
from _kozos import *  # noqa: F401,F403
from openpyxl.formatting.rule import FormulaRule

SKALA = [  # szint, személy, berendezés/termelés, projekt, valószínűség (veszély), valószínűség (projektkockázat)
    (5, "halál vagy maradandó egészségkárosodás", "a cella hetekig áll; > 10 MFt kár", "a projekt célja meghiúsul; > 30% költség- vagy 6 hónapnál nagyobb csúszás",
     "gyakori: legalább havonta (> 10/év)", "szinte biztos (> 80%)"),
    (4, "súlyos sérülés, kórházi ellátás, tartós munkaképtelenség", "napokig tartó leállás; 1–10 MFt kár", "jelentős: 10–30% költség- vagy 3–6 hónap csúszás",
     "valószínű: évente néhányszor (1–10/év)", "valószínű (50–80%)"),
    (3, "orvosi ellátást igénylő sérülés", "műszaknyi leállás; 0,1–1 MFt kár", "közepes: 5–10% költség- vagy 1–3 hónap csúszás",
     "alkalmi: néhány évente (0,1–1/év)", "lehetséges (20–50%)"),
    (2, "elsősegéllyel ellátható sérülés", "órás leállás; < 0,1 MFt kár", "kicsi: < 5% költség- vagy < 1 hónap csúszás",
     "ritka: az élettartam alatt előfordulhat (0,01–0,1/év)", "kevéssé valószínű (5–20%)"),
    (1, "sérülés nélküli esemény", "nincs érdemi kár", "elhanyagolható",
     "valószínűtlen: nem várható (< 0,01/év)", "valószínűtlen (< 5%)"),
]
PIROS, NARANCS, ZOLD = "F6DEDE", "FBE7D9", "DDEFE4"


def skala_lap(wb):
    ws = wb.create_sheet("Skálák")
    cimsor(ws, "Súlyossági és valószínűségi skála, zónahatárok",
           "A skálát a projekthez kell igazítani és egy ismert forgatókönyvvel kalibrálni; a zónahatárokat a vezetés hagyja jóvá.")
    tablazat(ws, 4, ["Szint", "Súlyosság: személy", "Súlyosság: berendezés, termelés", "Súlyosság: projekt",
                     "Valószínűség: veszély (egy rendszerre)", "Valószínűség: projektkockázat"],
             [7, 34, 30, 40, 36, 26], SKALA, bemeneti_oszlopok=(2, 3, 4, 5, 6))
    szoveg(ws["A11"], "Zónahatárok (S + P összege alapján)", felkov=True)
    szoveg(ws["A12"], "Elfogadhatatlan, ha S + P legalább:")
    bemenet(ws["D12"], 8)
    szoveg(ws["A13"], "ALARP (tűrhető), ha S + P legalább:")
    bemenet(ws["D13"], 6)
    szoveg(ws["A14"], "Különben: elfogadható.")
    megjegyzes(ws["D12"], "Az S + P összegen alapuló zónázás garantálja, hogy a mátrixban egy lépés legfeljebb egy zónahatárt lépjen át (Cox, 2008).")
    for r in (12, 13, 14):
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
    return ws


def zona(s, p):
    return (f'=IF(OR({s}="",{p}=""),"",IF({s}+{p}>=Skálák!$D$12,"elfogadhatatlan",'
            f'IF({s}+{p}>=Skálák!$D$13,"ALARP","elfogadható")))')


def zona_szinezes(ws, tartomany, elso_cella):
    for szo, szin in (("elfogadhatatlan", PIROS), ("ALARP", NARANCS), ("elfogadható", ZOLD)):
        ws.conditional_formatting.add(tartomany, FormulaRule(formula=[f'{elso_cella}="{szo}"'], fill=PatternFill("solid", fgColor=szin)))


def matrix_racs(ws, r0, c0, cim, s_tartomany, p_tartomany):
    """5x5 rács: a cellákban a kockázatok száma; színezés a küszöbök szerint."""
    szoveg(ws.cell(row=r0, column=c0), cim, felkov=True)
    szoveg(ws.cell(row=r0 + 1, column=c0), "S \\ P", felkov=True)
    for j in range(1, 6):
        c = ws.cell(row=r0 + 1, column=c0 + j, value=j)
        c.font = fej_font; c.fill = fej_fill; c.alignment = kozep
    for i, s in enumerate(range(5, 0, -1)):
        r = r0 + 2 + i
        c = ws.cell(row=r, column=c0, value=s)
        c.font = fej_font; c.fill = fej_fill; c.alignment = kozep
        for j in range(1, 6):
            cc = ws.cell(row=r, column=c0 + j)
            keplet(cc, f'=IF(COUNTIFS({s_tartomany},{s},{p_tartomany},{j})=0,"",COUNTIFS({s_tartomany},{s},{p_tartomany},{j}))', "0")
            cc.alignment = kozep
    ca, cz = get_column_letter(c0), get_column_letter(c0 + 5)
    cb = get_column_letter(c0 + 1)
    rng = f"{cb}{r0 + 2}:{cz}{r0 + 6}"
    for kif, szin in ((f"${ca}{r0 + 2}+{cb}${r0 + 1}>=Skálák!$D$12", PIROS),
                      (f"AND(${ca}{r0 + 2}+{cb}${r0 + 1}>=Skálák!$D$13,${ca}{r0 + 2}+{cb}${r0 + 1}<Skálák!$D$12)", NARANCS),
                      (f"${ca}{r0 + 2}+{cb}${r0 + 1}<Skálák!$D$13", ZOLD)):
        ws.conditional_formatting.add(rng, FormulaRule(formula=[kif], fill=PatternFill("solid", fgColor=szin)))
    for j in range(c0, c0 + 6):
        ws.column_dimensions[get_column_letter(j)].width = 9
