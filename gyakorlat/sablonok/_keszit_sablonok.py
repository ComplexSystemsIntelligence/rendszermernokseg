#!/usr/bin/env python3
"""A Gyakorlati útmutató Excel-sablonjainak előállítása.

Futtatás:  python3 gyakorlat/sablonok/_keszit_sablonok.py
Minden számított cella képlet, így a sablonok kitöltéskor újraszámolnak.
"""
import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import Reference, ScatterChart, Series
from openpyxl.chart.label import DataLabelList
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

MAPPA = Path(__file__).resolve().parent
KEK = "285780"
HALVANY = "E6EEF6"
SARGA = "FFF4CC"
BETU = "Arial"

fej_font = Font(name=BETU, bold=True, color="FFFFFF")
fej_fill = PatternFill("solid", fgColor=KEK)
cim_font = Font(name=BETU, bold=True, size=14, color=KEK)
alap_font = Font(name=BETU, size=10)
bevitel_font = Font(name=BETU, size=10, color="0000FF")
bevitel_fill = PatternFill("solid", fgColor=SARGA)
keplet_fill = PatternFill("solid", fgColor=HALVANY)
vekony = Side(style="thin", color="C9D6E3")
keret = Border(left=vekony, right=vekony, top=vekony, bottom=vekony)
tord = Alignment(wrap_text=True, vertical="top")


def fejlec(ws, sor, cimek, szelessegek):
    for i, (c, w) in enumerate(zip(cimek, szelessegek), start=1):
        cell = ws.cell(row=sor, column=i, value=c)
        cell.font, cell.fill, cell.border = fej_font, fej_fill, keret
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[sor].height = 32


def cimsor(ws, szoveg, alcim=None):
    ws["A1"] = szoveg
    ws["A1"].font = cim_font
    if alcim:
        ws["A2"] = alcim
        ws["A2"].font = Font(name=BETU, size=10, italic=True, color="555555")


def utmutato(wb, cim, sorok):
    from _kozos import pe_logo
    ws = wb.active
    ws.title = "Útmutató"
    ws["A1"] = cim
    ws["A1"].font = cim_font
    pe_logo(ws)
    ws.column_dimensions["A"].width = 110
    for i, s in enumerate(sorok, start=3):
        c = ws.cell(row=i, column=1, value=s)
        c.font = Font(name=BETU, size=10, bold=s.startswith("■"))
        c.alignment = Alignment(wrap_text=True, vertical="top")
    jel = len(sorok) + 4
    ws.cell(row=jel, column=1, value="Jelmagyarázat:").font = Font(name=BETU, bold=True)
    c = ws.cell(row=jel + 1, column=1, value="Sárga háttér, kék betű: ide írj (bemenet)")
    c.fill, c.font = bevitel_fill, bevitel_font
    c = ws.cell(row=jel + 2, column=1, value="Halványkék háttér: képlet, ne írd felül")
    c.fill, c.font = keplet_fill, alap_font
    ws.cell(row=jel + 4, column=1,
            value="Forrás: Abonyi J.: Rendszermérnöki eszköztár – Gyakorlati útmutató (CC BY-NC-SA 4.0)").font = \
        Font(name=BETU, size=9, italic=True, color="777777")
    return ws


# ---------------------------------------------------------------------------
# 1. Érdekeltfél-nyilvántartás, hatalom–érdekeltség rács, fontossági modell
# ---------------------------------------------------------------------------
GYURUK = ["A mi rendszerünk", "Befoglaló rendszer", "Tágabb környezet"]
OSZTALYOK = ["Nem érdekelt", "Követelőző", "Mérlegelhető", "Függő",
             "Szunnyadó", "Veszélyes", "Domináns", "Meghatározó"]
EF_FEJ = ["Azonosító", "Érdekelt fél", "Hagymagyűrű", "Szerep", "Fő elvárások (igényként)",
          "Hatalom (1–5)", "Érdekeltség (1–5)", "Legitim követelés? (1/0)", "Sürgős? (1/0)",
          "Negyed", "Fontossági osztály", "Javasolt bevonás", "Kapcsolattartó", "Csatorna, gyakoriság"]
EF_SZEL = [10, 26, 18, 18, 42, 10, 11, 11, 9, 15, 15, 24, 16, 22]

VB_PELDA = [
    ("Önkormányzat", "Befoglaló rendszer", "szponzor, megrendelő", "A belvárosi autós forgalom csökkenjen; a rendszer politikailag vállalható és fenntartható legyen", 5.0, 4.8, 1, 1),
    ("Üzemeltető konzorcium", "Befoglaló rendszer", "üzemeltető, pénzügyi haszonélvező", "Kiszámítható bevétel, alacsony áthelyezési és javítási költség", 4.3, 4.6, 1, 1),
    ("Közlekedési társaság", "Befoglaló rendszer", "kapcsolódó rendszer", "Illeszkedés a bérletrendszerhez és az átszállópontokhoz", 3.6, 3.3, 1, 0),
    ("Egyetem", "Befoglaló rendszer", "kimenet haszonélvezője", "A kampuszok közötti közlekedés legyen gyors és olcsó a hallgatóknak", 3.2, 3.9, 1, 0),
    ("Diák felhasználók", "A mi rendszerünk", "napi kezelő (felhasználó)", "Esti és hétvégi elérhetőség, mobilos fizetés, alacsony díj", 1.9, 4.5, 1, 1),
    ("Akadálymentességi érdekképviselet", "Tágabb környezet", "szabályozó (társadalmi)", "A dokkolók ne szűkítsék a járdát; legyen segítségkérési lehetőség", 1.6, 4.1, 1, 1),
    ("Környezetvédő civilek", "Tágabb környezet", "politikai haszonélvező", "Mérhető kibocsátáscsökkentés, átlátható adatok", 1.25, 3.45, 1, 0),
    ("Gyalogosok, boltosok", "Tágabb környezet", "negatív érdekelt", "Szabad járda, ne legyen kerékpár a kirakatok előtt", 1.7, 2.6, 1, 0),
    ("Helyi média", "Tágabb környezet", "politikai haszonélvező", "Hírértékű, látható eredmények vagy problémák", 2.3, 1.6, 0, 0),
    ("Energiaszolgáltató", "Tágabb környezet", "beszállító", "Szabványos hálózati csatlakozás, kiszámítható terhelés", 3.4, 1.4, 1, 0),
    ("Közlekedési hatóság", "Tágabb környezet", "szabályozó", "Közúti és közterületi szabályok betartása", 4.5, 1.9, 1, 0),
    ("Rendőrség", "Tágabb környezet", "szabályozó", "Lopások, balesetek és rendbontás megelőzése", 3.5, 2.1, 1, 0),
]


def ef_kepletek(ws, r):
    ws[f"J{r}"] = (f'=IF(OR(F{r}="",G{r}=""),"",IF(AND(F{r}>=3,G{r}>=3),"Kulcsszereplő",'
                   f'IF(G{r}>=3,"Érintett",IF(F{r}>=3,"Keretadó","Tömeg"))))')
    ws[f"K{r}"] = (f'=IF(OR(F{r}="",H{r}="",I{r}=""),"",CHOOSE((F{r}>=3)*4+H{r}*2+I{r}+1,'
                   + ",".join(f'"{o}"' for o in OSZTALYOK) + "))")
    ws[f"L{r}"] = (f'=IF(J{r}="","",IF(J{r}="Kulcsszereplő","Szoros együttműködés, közös döntés",'
                   f'IF(J{r}="Érintett","Tájékoztatás és bevonás",IF(J{r}="Keretadó",'
                   f'"Elégedettség fenntartása","Figyelemmel kísérés"))))')


def ef_lap(wb, nev, adatok, uressorok):
    ws = wb.create_sheet(nev)
    cimsor(ws, "Érdekeltfél-nyilvántartás", "Egy sor = egy érdekelt fél (szerep). A hatalom és az érdekeltség 1–5 skálán; a negyed és a fontossági osztály képlettel számolódik.")
    fejlec(ws, 4, EF_FEJ, EF_SZEL)
    r = 5
    for i, (nev_, gyuru, szerep, elv, h, e, leg, sur) in enumerate(adatok, start=1):
        for c, v in zip("ABCDEFGHI", [f"EF-{i:02d}", nev_, gyuru, szerep, elv, h, e, leg, sur]):
            ws[f"{c}{r}"] = v
        ef_kepletek(ws, r)
        r += 1
    for _ in range(uressorok):
        ef_kepletek(ws, r)
        r += 1
    utolso = r - 1
    for row in ws.iter_rows(min_row=5, max_row=utolso, max_col=len(EF_FEJ)):
        for cell in row:
            cell.border, cell.alignment = keret, tord
            if cell.column <= 9 or cell.column >= 13:
                cell.font, cell.fill = bevitel_font, bevitel_fill
            else:
                cell.font, cell.fill = alap_font, keplet_fill
    dv_gy = DataValidation(type="list", formula1='"' + ",".join(GYURUK) + '"', allow_blank=True)
    dv_sk = DataValidation(type="decimal", operator="between", formula1="1", formula2="5", allow_blank=True)
    dv_01 = DataValidation(type="whole", operator="between", formula1="0", formula2="1", allow_blank=True)
    for dv, rng in [(dv_gy, f"C5:C{utolso}"), (dv_sk, f"F5:G{utolso}"), (dv_01, f"H5:I{utolso}")]:
        ws.add_data_validation(dv)
        dv.add(rng)
    ws.freeze_panes = "C5"
    ws["F4"].comment = Comment("Hatalom: döntési jogkör, nélkülözhetetlen erőforrás, mozgósítóképesség. 1 = alig, 5 = döntő.", "sablon")
    ws["G4"].comment = Comment("Érdekeltség: mennyire változtatja meg a rendszer a mindennapjait vagy eredményét, mennyire foglalkozik vele aktívan.", "sablon")
    ws["H4"].comment = Comment("Legitim-e a követelése (jog, szerződés, erkölcsi alap)? 1 = igen, 0 = nem.", "sablon")
    ws["I4"].comment = Comment("Időkritikus és fontos-e számára a követelése? 1 = igen, 0 = nem.", "sablon")
    ws["K4"].comment = Comment("Mitchell–Agle–Wood (1997) fontossági modellje; a hatalom akkor számít meglévőnek, ha legalább 3.", "sablon")
    # színkód a negyedekhez
    for szoveg, szin in [("Kulcsszereplő", "FBE7D9"), ("Érintett", "DDEFE4"), ("Keretadó", "DCE7F2")]:
        ws.conditional_formatting.add(f"J5:J{utolso}", FormulaRule(formula=[f'$J5="{szoveg}"'], fill=PatternFill("solid", fgColor=szin)))
    return ws, utolso


def racs_diagram(ws, utolso, hely):
    ch = ScatterChart()
    ch.title = "Hatalom–érdekeltség rács"
    ch.style = 13
    ch.x_axis.title = "Hatalom (1–5)"
    ch.y_axis.title = "Érdekeltség (1–5)"
    ch.x_axis.scaling.min, ch.x_axis.scaling.max = 0.5, 5.5
    ch.y_axis.scaling.min, ch.y_axis.scaling.max = 0.5, 5.5
    ch.x_axis.majorUnit = ch.y_axis.majorUnit = 1
    x = Reference(ws, min_col=6, min_row=5, max_row=utolso)
    y = Reference(ws, min_col=7, min_row=5, max_row=utolso)
    s = Series(y, x, title="Érdekelt felek")
    s.marker.symbol = "circle"
    s.marker.size = 8
    s.marker.graphicalProperties.solidFill = "3E8E63"
    s.graphicalProperties.line.noFill = True
    ch.series.append(s)
    ch.legend = None
    ch.roundedCorners = False
    ch.title.overlay = False
    ch.x_axis.title.overlay = False
    ch.y_axis.title.overlay = False
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.width, ch.height = 16, 12
    ws.add_chart(ch, hely)


def erdekelt_felek_sablon():
    wb = Workbook()
    utmutato(wb, "Érdekeltfél-elemzés – sablon", [
        "■ Mire való? Az érdekelt felek nyilvántartása, a hatalom–érdekeltség rács és a fontossági (szaliencia-) osztályozás egy helyen.",
        "■ 1. lépés – Azonosítás: a „Nyilvántartás” lapon minden érdekelt félnek (pontosabban szerepnek) egy sort tölts ki. Használd az életciklus-szakaszokat, a hagymamodell gyűrűit és az ellenőrző kérdéseket (Gyakorlati útmutató: Érdekelt felek azonosítása).",
        "■ 2. lépés – Pontozás: a hatalmat és az érdekeltséget 1–5 skálán pontozd. Csapatban először egymástól függetlenül pontozzatok, majd beszéljétek meg az eltéréseket.",
        "■ 3. lépés – Legitimitás és sürgősség: 1 = igen, 0 = nem. A fontossági osztályt a sablon számolja.",
        "■ 4. lépés – Bevonás: a javasolt bevonási mód a negyedből adódik; a kapcsolattartót, a csatornát és a gyakoriságot te add meg.",
        "■ A „Példa – VárosiBringa” lap a Kézikönyv 5. fejezetének kidolgozott példáját tartalmazza, kitöltve. A diagram a pontozásból automatikusan frissül.",
        "A negyedek határa a skála közepe (3). A negyedelnevezések Eden és Ackermann (1998), a fontossági osztályok Mitchell, Agle és Wood (1997) szerint.",
    ])
    ws, ut = ef_lap(wb, "Nyilvántartás", [VB_PELDA[0]], 39)
    ws["A5"].comment = Comment("Mintasor: írd felül a saját adataiddal.", "sablon")
    racs_diagram(ws, ut, "P4")
    wp, utp = ef_lap(wb, "Példa – VárosiBringa", VB_PELDA, 0)
    racs_diagram(wp, utp, "P4")
    wb.save(MAPPA / "erdekelt_felek_sablon.xlsx")


# ---------------------------------------------------------------------------
# 2. Kano-elemzés
# ---------------------------------------------------------------------------
VALASZOK = ["Tetszene", "Elvárom", "Közömbös", "Elviselném", "Nem tetszene"]
TABLA = [["K", "V", "V", "V", "E"],
         ["F", "Kö", "Kö", "Kö", "A"],
         ["F", "Kö", "Kö", "Kö", "A"],
         ["F", "Kö", "Kö", "Kö", "A"],
         ["F", "F", "F", "F", "K"]]
KANO_PELDA = [  # V, E, A, Kö, F, K
    ("Megbízható zár és kölcsönzés", (6, 22, 80, 10, 0, 2)),
    ("Valós idejű elérhetőség az alkalmazásban", (18, 62, 28, 10, 0, 2)),
    ("Közös bérlet a helyi buszokkal", (58, 24, 8, 26, 2, 2)),
    ("Telefontöltő a kormányon", (30, 10, 4, 70, 4, 2)),
    ("Hangjelzés a kerékpár indulásakor", (6, 6, 4, 54, 46, 4)),
]
KAT_PAR = {"V": (1, 3), "E": (1, 5), "A": (2, 5), "Kö": (3, 3), "F": (5, 3), "K": (1, 1)}
KATEG = ["V", "E", "A", "Kö", "F", "K"]
KAT_NEV = {"V": "vonzó", "E": "egydimenziós", "A": "alapvető", "Kö": "közömbös", "F": "fordított", "K": "kétséges"}


def kano_sablon():
    random.seed(20261120)
    wb = Workbook()
    utmutato(wb, "Kano-elemzés – sablon", [
        "■ Mire való? Az érdekelt felek elvárásainak osztályozása alapvető (A), egydimenziós (E), vonzó (V), közömbös (Kö), fordított (F) és kétséges (K) kategóriákba, valamint az elégedettségi együtthatók (CS+, CS−) kiszámítása.",
        "■ 1. lépés – A „Jellemzők” lapon sorold fel a vizsgált jellemzőket (legfeljebb 5), és fogalmazd meg a funkcionális és a diszfunkcionális kérdést.",
        "■ 2. lépés – A „Válaszok” lapra írd be a kérdőív válaszait kódolva: 1 = Tetszene, 2 = Elvárom, 3 = Közömbös, 4 = Elviselném, 5 = Nem tetszene. Jellemzőnként két oszlop: funkcionális (F) és diszfunkcionális (D).",
        "■ 3. lépés – A kategória oszlop a „Kiértékelő tábla” alapján automatikusan kitöltődik; az „Összesítés” lap jellemzőnként megadja a darabszámokat, a leggyakoribb kategóriát és az együtthatókat.",
        "■ A sablon a Kézikönyv 5. fejezetének VárosiBringa-példájával van feltöltve (120 válaszadó, szemléltető adatok). Töröld a válaszokat, és írd be a sajátjaidat.",
        "Képletek (Berger és mtsai, 1993): CS+ = (V+E)/(V+E+A+Kö); CS− = −(E+A)/(V+E+A+Kö). A fordított és a kétséges válaszok nem számítanak bele.",
    ])
    # Kiértékelő tábla
    kt = wb.create_sheet("Kiértékelő tábla")
    cimsor(kt, "Kano-kiértékelő tábla", "Sor: funkcionális válasz; oszlop: diszfunkcionális válasz (Berger és mtsai, 1993)")
    kt["A4"] = "Funkcionális \\ diszfunkcionális"
    kt["A4"].font, kt["A4"].fill = fej_font, fej_fill
    kt.column_dimensions["A"].width = 30
    for j, v in enumerate(VALASZOK, start=2):
        c = kt.cell(row=4, column=j, value=f"{j-1} – {v}")
        c.font, c.fill, c.alignment = fej_font, fej_fill, Alignment(horizontal="center", wrap_text=True)
        kt.column_dimensions[get_column_letter(j)].width = 15
    for i, v in enumerate(VALASZOK, start=5):
        c = kt.cell(row=i, column=1, value=f"{i-4} – {v}")
        c.font, c.fill = Font(name=BETU, bold=True), keplet_fill
        for j in range(5):
            cc = kt.cell(row=i, column=j + 2, value=TABLA[i - 5][j])
            cc.font, cc.alignment, cc.border = alap_font, Alignment(horizontal="center"), keret
    kt["A11"] = "V = vonzó, E = egydimenziós, A = alapvető, Kö = közömbös, F = fordított, K = kétséges"
    kt["A11"].font = Font(name=BETU, size=9, italic=True)

    # Jellemzők
    jl = wb.create_sheet("Jellemzők")
    cimsor(jl, "Vizsgált jellemzők és kérdések")
    fejlec(jl, 4, ["Kód", "Jellemző", "Funkcionális kérdés", "Diszfunkcionális kérdés"], [8, 36, 60, 60])
    for i, (nev, _) in enumerate(KANO_PELDA, start=1):
        r = 4 + i
        vals = [f"J{i}", nev, f"Mit érezne, ha a rendszerben megvalósulna: {nev.lower()}?",
                f"Mit érezne, ha a rendszerben nem valósulna meg: {nev.lower()}?"]
        for c, v in zip("ABCD", vals):
            cell = jl[f"{c}{r}"]
            cell.value = v
            cell.font, cell.fill, cell.border, cell.alignment = bevitel_font, bevitel_fill, keret, tord

    # Válaszok (válaszadónkénti adatsor a példa összesítéseiből)
    va = wb.create_sheet("Válaszok")
    cimsor(va, "Kérdőív-válaszok (kódolva: 1–5)", "Jellemzőnként: F = funkcionális, D = diszfunkcionális válasz, Kat. = kategória (képlet)")
    va.cell(row=4, column=1, value="Válaszadó").font = fej_font
    va.cell(row=4, column=1).fill = fej_fill
    va.column_dimensions["A"].width = 11
    N = 120
    MAXSOR = 300
    oszlopok = []
    for k, (nev, szamok) in enumerate(KANO_PELDA):
        cF, cD, cK = 2 + 3 * k, 3 + 3 * k, 4 + 3 * k
        oszlopok.append((cF, cD, cK))
        for cc, t in zip((cF, cD, cK), (f"J{k+1} F", f"J{k+1} D", f"J{k+1} Kat.")):
            cell = va.cell(row=4, column=cc, value=t)
            cell.font, cell.fill, cell.alignment = fej_font, fej_fill, Alignment(horizontal="center")
            va.column_dimensions[get_column_letter(cc)].width = 7.5
        lista = []
        for kat, db in zip(KATEG, szamok):
            lista += [kat] * db
        random.shuffle(lista)
        for r in range(MAXSOR):
            sor = 5 + r
            if r < N:
                f_, d_ = KAT_PAR[lista[r]]
                va.cell(row=sor, column=cF, value=f_)
                va.cell(row=sor, column=cD, value=d_)
            lF, lD = get_column_letter(cF), get_column_letter(cD)
            va.cell(row=sor, column=cK,
                    value=f"=IF(OR({lF}{sor}=\"\",{lD}{sor}=\"\"),\"\",INDEX('Kiértékelő tábla'!$B$5:$F$9,{lF}{sor},{lD}{sor}))")
    for r in range(MAXSOR):
        sor = 5 + r
        va.cell(row=sor, column=1, value=r + 1).font = alap_font
        for (cF, cD, cK) in oszlopok:
            for cc in (cF, cD):
                c = va.cell(row=sor, column=cc)
                c.font, c.fill, c.alignment = bevitel_font, bevitel_fill, Alignment(horizontal="center")
            c = va.cell(row=sor, column=cK)
            c.font, c.fill, c.alignment = alap_font, keplet_fill, Alignment(horizontal="center")
    dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True)
    va.add_data_validation(dv)
    for (cF, cD, _) in oszlopok:
        dv.add(f"{get_column_letter(cF)}5:{get_column_letter(cD)}{4+MAXSOR}")
    va.freeze_panes = "B5"

    # Összesítés
    os_ = wb.create_sheet("Összesítés")
    cimsor(os_, "Kano-összesítés", "A darabszámok, a besorolás és az együtthatók képlettel számolódnak a „Válaszok” lapból.")
    fej = ["Kód", "Jellemző", "V", "E", "A", "Kö", "F", "K", "Válaszok", "Leggyakoribb", "Besorolás", "CS+", "CS−", "|CS−|"]
    fejlec(os_, 4, fej, [7, 40, 7, 7, 7, 7, 7, 7, 10, 13, 15, 9, 9, 9])
    for k, (_, _) in enumerate(KANO_PELDA):
        r = 5 + k
        _, _, cK = oszlopok[k]
        rng = f"Válaszok!${get_column_letter(cK)}$5:${get_column_letter(cK)}${4+MAXSOR}"
        os_[f"A{r}"] = f"J{k+1}"
        os_[f"B{r}"] = f"=Jellemzők!B{5+k}"
        for j, kat in enumerate(KATEG):
            col = get_column_letter(3 + j)
            os_[f"{col}{r}"] = f'=COUNTIF({rng},"{kat}")'
        os_[f"I{r}"] = f"=SUM(C{r}:H{r})"
        os_[f"J{r}"] = f'=IF(I{r}=0,"",INDEX($C$4:$H$4,MATCH(MAX(C{r}:H{r}),C{r}:H{r},0)))'
        os_[f"K{r}"] = (f'=IF(J{r}="","",IF(J{r}="V","vonzó",IF(J{r}="E","egydimenziós",IF(J{r}="A","alapvető",'
                        f'IF(J{r}="Kö","közömbös",IF(J{r}="F","fordított","kétséges"))))))')
        os_[f"L{r}"] = f"=IF(SUM(C{r}:F{r})=0,\"\",(C{r}+D{r})/SUM(C{r}:F{r}))"
        os_[f"M{r}"] = f"=IF(SUM(C{r}:F{r})=0,\"\",-(D{r}+E{r})/SUM(C{r}:F{r}))"
        os_[f"N{r}"] = f"=IF(M{r}=\"\",\"\",ABS(M{r}))"
        for c in range(1, 15):
            cell = os_.cell(row=r, column=c)
            cell.font, cell.fill, cell.border = alap_font, keplet_fill, keret
        for col in "LMN":
            os_[f"{col}{r}"].number_format = "0.00"
    os_["B11"] = "Értelmezés: CS+ közel 1 → a jellemző megléte erősen növeli az elégedettséget; CS− közel −1 → hiánya erős elégedetlenséget okoz."
    os_["B11"].font = Font(name=BETU, size=9, italic=True)
    os_["B12"] = "Ha két kategória gyakorisága közel azonos, elemezd külön a felhasználói csoportokat."
    os_["B12"].font = Font(name=BETU, size=9, italic=True)
    # elégedettségi diagram (Better–Worse)
    ch = ScatterChart()
    ch.title = "Elégedettségi diagram (CS+ és |CS−|)"
    ch.style = 13
    ch.x_axis.title = "|CS−| – a hiány okozta elégedetlenség"
    ch.y_axis.title = "CS+ – a megléttel járó elégedettség"
    for ax in (ch.x_axis, ch.y_axis):
        ax.scaling.min, ax.scaling.max, ax.majorUnit = 0, 1, 0.25
        ax.number_format = "0.00"
    s = Series(Reference(os_, min_col=12, min_row=5, max_row=9), Reference(os_, min_col=14, min_row=5, max_row=9), title="Jellemzők")
    s.marker.symbol = "circle"
    s.marker.size = 9
    s.marker.graphicalProperties.solidFill = KEK
    s.graphicalProperties.line.noFill = True
    s.dLbls = DataLabelList()
    s.dLbls.showVal = False
    s.dLbls.showSerName = False
    ch.series.append(s)
    ch.legend = None
    ch.roundedCorners = False
    ch.title.overlay = False
    ch.x_axis.title.overlay = False
    ch.y_axis.title.overlay = False
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.width, ch.height = 15, 11
    os_.add_chart(ch, "B14")
    os_["P14"] = "A diagram negyedei: jobb felső = egydimenziós, bal felső = vonzó, jobb alsó = alapvető, bal alsó = közömbös (0,5-ös határral)."
    os_["P14"].font = Font(name=BETU, size=9, italic=True)
    wb.save(MAPPA / "kano_sablon.xlsx")


# ---------------------------------------------------------------------------
# 3. Projekt V-terve
# ---------------------------------------------------------------------------
V_LEPESEK = [
    ("1", "Probléma, cél, működési koncepció", "Problémaleírás, szükséglet–cél–célkitűzés, működési forgatókönyvek", "Átadás, üzemeltetés", "A célkitűzések (MOE) mérése próbaüzemben"),
    ("2", "Az érdekelt felek igényei", "Érdekeltfél-nyilvántartás, rács, validált elvárások, Kano-elemzés", "Validáció", "Felhasználói próba a fő érdekelt csoportokkal"),
    ("3", "Rendszerkövetelmények", "Mérhető követelmények (MOE/MOP/TPM), QFD", "Rendszerverifikáció", "Követelményenkénti verifikációs mód (teszt, elemzés, szemle, bemutatás)"),
    ("4", "Architektúra és koncepció", "Funkció–forma dekompozíció, koncepcióváltozatok, Pugh/hasznosság", "Integráció", "Integrációs sorrend és interfészellenőrzések"),
    ("5", "Részletes tervezés", "Részletes terv, emberi tényezők, FMEA", "Komponens-verifikáció", "Komponensszintű vizsgálatok listája"),
    ("6", "Megvalósítás", "Folyamatmodell (BPMN), kapacitás, OEE-terv", "–", "–"),
]


def v_terv_sablon():
    wb = Workbook()
    utmutato(wb, "Projekt V-terve – sablon", [
        "■ Mire való? A féléves projekt (vagy bármely fejlesztés) teljes ívének egyoldalas áttekintése a V-modell mentén.",
        "■ Minden bal ági lépéshez rögzítsd a munkaterméket, és ugyanabban a sorban azt is, hogyan fogod a jobb ágon ellenőrizni. Ez a „korai tesztterv”.",
        "■ A „Felülvizsgálatok” lapon jelölj ki legalább három ellenőrzési pontot belépési feltételekkel.",
        "■ A kitöltött mintasorok általános útmutatók; írd át őket a saját projektedre.",
    ])
    ws = wb.create_sheet("V-terv")
    cimsor(ws, "A projekt V-terve", "Projekt: ……………………   Csapat: ……………………   Változat/dátum: ……………")
    fejlec(ws, 4, ["Szint", "Bal ág: lépés", "Munkatermék (mit adunk le?)", "Jobb ági pár", "Hogyan ellenőrizzük?", "Felelős", "Határidő"],
           [7, 30, 46, 22, 46, 16, 12])
    for i, sor in enumerate(V_LEPESEK, start=5):
        for j, v in enumerate(sor, start=1):
            c = ws.cell(row=i, column=j, value=v)
            c.border, c.alignment = keret, tord
            c.font, c.fill = bevitel_font, bevitel_fill
        for j in (6, 7):
            c = ws.cell(row=i, column=j)
            c.border, c.font, c.fill = keret, bevitel_font, bevitel_fill
        ws.cell(row=i, column=7).number_format = "yyyy.mm.dd"
        ws.row_dimensions[i].height = 42
    fv = wb.create_sheet("Felülvizsgálatok")
    cimsor(fv, "Felülvizsgálati pontok")
    fejlec(fv, 4, ["Felülvizsgálat", "Kulcskérdés", "Belépési feltételek (milyen dokumentumok, eredmények kellenek?)", "Résztvevők", "Időpont", "Döntés / nyitott kérdések"],
           [24, 40, 50, 22, 12, 40])
    minta = [("Koncepció és követelmények", "Értjük-e a problémát, és mérhetők-e a követelmények?", "Érdekeltfél-elemzés, célkitűzések, követelménylista verifikációs módokkal"),
             ("Terv", "Teljesítheti-e a kiválasztott koncepció a követelményeket elfogadható kockázattal?", "Koncepció-összevetés, architektúra, FMEA"),
             ("Átadás előtti ellenőrzés", "Igazoltuk-e a követelményeket, és elfogadják-e a felhasználók?", "Verifikációs mátrix, validációs eredmények, folyamatmodell")]
    for i, (a, b, c_) in enumerate(minta, start=5):
        for j, v in enumerate([a, b, c_, "", "", ""], start=1):
            cell = fv.cell(row=i, column=j, value=v)
            cell.border, cell.alignment, cell.font, cell.fill = keret, tord, bevitel_font, bevitel_fill
        fv.row_dimensions[i].height = 44
    wb.save(MAPPA / "projekt_v_terv_sablon.xlsx")


if __name__ == "__main__":
    erdekelt_felek_sablon()
    kano_sablon()
    v_terv_sablon()
    print("Sablonok elkészültek:", ", ".join(p.name for p in sorted(MAPPA.glob("*.xlsx"))))
