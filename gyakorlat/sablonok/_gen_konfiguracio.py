"""Konfigurációkezelés: konfigurációs elemek, hatáskapcsolatok, változáskérelmek (eszközlap: Konfigurációkezelés és változáskérelem)."""
from openpyxl.formatting.rule import CellIsRule, FormulaRule

from _konfiguracio_adat import CI, ERTEKELES, HATAS_JELLEMZOK, KAPCSOLATOK, VK
from _kozos import *  # noqa: F401,F403

NCI, NVK = 25, 20
R0 = 5                      # az első adatsor a CI-, kapcsolat- és hatáslapokon
RU = R0 + NCI - 1           # az utolsó CI-sor
B2 = 35                     # a javasolt ellenőrzések blokkjának első sora
SZURKE = PatternFill("solid", fgColor="E5E5E5")
NARANCS = PatternFill("solid", fgColor="F8DDB4")
PIROS = PatternFill("solid", fgColor="F6D5D5")
HALVANY = PatternFill("solid", fgColor="DCE7F2")
CI_LAP, K_LAP, H_LAP, V_LAP, O_LAP = "Konfigurációs elemek", "Kapcsolatok", "Hatásmátrix", "Változáskérelmek", "Összesítés"


def oszl(i):
    """A mátrixok i-edik (0-alapú) oszlopa: C, D, ..."""
    return get_column_letter(3 + i)


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Konfigurációkezelés és változáskérelmek – sablon", [
        "■ Mire való? A konfigurációs elemek (dokumentumok, szoftverek, hardverek, adatok) nyilvántartása, a köztük lévő "
        "hatáskapcsolatok rögzítése és a változáskérelmek kezelése: besorolás (jelentős / kisebb), döntéshozó, hatáselemzés, átfutási idő.",
        "■ Konfigurációs elemek: azonosító, megnevezés, típus, alapvonal, változat, állapot, felelős, tárolás helye. "
        "Az utolsó oszlopok mutatják, hány nyitott kérelem érinti az elemet, és hány másik elemre hat.",
        "■ Kapcsolatok: x a sor és az oszlop metszéspontjában, ha a sorban álló elem módosítása után az oszlopban állót ellenőrizni kell.",
        "■ Változáskérelmek: a hat hatásjellemző (alapvonal/specifikáció, költség, biztonság, interfész, képzés, leszállított termék) "
        "bármelyike „igen”, a változás jelentős, és a konfigurációs bizottság dönt róla; egyébként kisebb, és a konfigurációs vezető dönt. "
        "Az eltérési engedély nem változtatja meg az alapvonalat.",
        "■ Hatásmátrix: x = módosítandó elem, n = megvizsgálva, nem érinti. Az alsó blokk ? jellel jelöli azokat az elemeket, amelyekre "
        "egy módosítandó elem közvetlenül hat, de a hatáselemzés még nem vizsgálta őket. (A több lépésen át terjedő hatásokat a notebook számolja.)",
        "■ Összesítés: a kérelmek száma osztály és állapot szerint, átfutási idők, kiegészítendő hatáselemzések.",
        "A kitöltött példa a KoboCella konfigurációkezelése (kézikönyv 26. fejezet).",
        "Források: ISO 10007:2017; MIL-HDBK-61B (2020); NASA Systems Engineering Handbook (2016), 6.5. szakasz.",
    ])

    # ---- Konfigurációs elemek
    wc = wb.create_sheet(CI_LAP)
    cimsor(wc, "Konfigurációs elemek", "A nyilvántartás (configuration status accounting) alapja: minden elem azonosítóval, változattal és felelőssel.")
    fej = ["Az.", "Megnevezés", "Típus", "Alapvonal", "Változat", "Állapot", "Felelős", "Tárolás helye",
           "Nyitott kérelmek (db)", "Hat (db elemre)", "Rá hat (db elem)"]
    utc = tablazat(
        wc, R0 - 1, fej, [8, 40, 12, 13, 9, 15, 22, 18, 11, 10, 10], [list(x) for x in CI],
        bemeneti_oszlopok=tuple(range(1, 9)),
        kepletek={
            9: lambda r: (f"=IF(A{r}=\"\",\"\",SUMPRODUCT(('{H_LAP}'!$C{r}:${oszl(NVK - 1)}{r}=\"x\")*"
                          f"(('{H_LAP}'!$C$30:${oszl(NVK - 1)}$30=\"döntésre vár\")+('{H_LAP}'!$C$30:${oszl(NVK - 1)}$30=\"végrehajtás alatt\"))))"),
            10: lambda r: f"=IF(A{r}=\"\",\"\",COUNTIF('{K_LAP}'!$C{r}:${oszl(NCI - 1)}{r},\"x\"))",
            11: lambda r: f"=IF(A{r}=\"\",\"\",COUNTIF('{K_LAP}'!{oszl(r - R0)}${R0}:{oszl(r - R0)}${RU},\"x\"))",
        },
        uressor=NCI - len(CI))
    assert utc == RU
    legordulo(wc, f"C{R0}:C{RU}", ["dokumentum", "szoftver", "hardver", "adat", "modell"])
    legordulo(wc, f"D{R0}:D{RU}", ["funkcionális", "allokált", "termék"])
    legordulo(wc, f"F{R0}:F{RU}", ["tervezet", "alapvonalban", "módosítás alatt", "visszavont"])
    wc.conditional_formatting.add(f"I{R0}:I{RU}", CellIsRule(operator="greaterThan", formula=["0"], fill=NARANCS))
    wc.freeze_panes = f"C{R0}"

    # ---- Kapcsolatok (CI × CI)
    wk = wb.create_sheet(K_LAP)
    cimsor(wk, "Hatáskapcsolatok", "x: a sorban álló elem módosítása után az oszlopban álló elemet ellenőrizni kell.")
    wk.column_dimensions["A"].width, wk.column_dimensions["B"].width = 8, 34
    fejlec(wk, R0 - 1, ["Az.", "Megnevezés"], [8, 34])
    idx = {c[0]: i for i, c in enumerate(CI)}
    for j in range(NCI):
        c = wk.cell(row=R0 - 1, column=3 + j)
        keplet(c, f"=IF('{CI_LAP}'!A{R0 + j}=\"\",\"\",'{CI_LAP}'!A{R0 + j})")
        c.font, c.fill, c.alignment = fej_font, fej_fill, Alignment(text_rotation=90, horizontal="center")
        wk.column_dimensions[oszl(j)].width = 4.2
    wk.row_dimensions[R0 - 1].height = 44
    for i in range(NCI):
        r = R0 + i
        keplet(wk.cell(row=r, column=1), f"=IF('{CI_LAP}'!A{r}=\"\",\"\",'{CI_LAP}'!A{r})")
        keplet(wk.cell(row=r, column=2), f"=IF('{CI_LAP}'!B{r}=\"\",\"\",'{CI_LAP}'!B{r})")
        forras = CI[i][0] if i < len(CI) else None
        for j in range(NCI):
            c = wk.cell(row=r, column=3 + j)
            if i == j:
                c.fill, c.border = SZURKE, keret
                continue
            cel = CI[j][0] if j < len(CI) else None
            bemenet(c, "x" if forras and cel and cel in KAPCSOLATOK.get(forras, []) else None)
            c.alignment = kozep
    legordulo(wk, f"C{R0}:{oszl(NCI - 1)}{RU}", ["x"])
    wk.freeze_panes = f"C{R0}"

    # ---- Változáskérelmek
    wv = wb.create_sheet(V_LAP)
    cimsor(wv, "Változáskérelmek és eltérési engedélyek",
           "A sárga cellákat töltsd ki; a besorolás, a döntéshozó, az állapot és az átfutás számított.")
    hj = HATAS_JELLEMZOK
    fej = (["Az.", "Cím", "Fajta", "Kezdeményező", "Beadva"] + hj +
           ["Osztály", "Döntéshozó", "Döntés", "Döntés dátuma", "Lezárva", "Állapot", "Döntésig (nap)", "Átfutás (nap)",
            "Nyitva (nap)", "Módosítandó CI (db)", "Ellenőrizetlen CI (db)", "Figyelmeztetés"])
    sorok = [[v[0], v[1], v[2], v[3], v[4]] + v[5] + [None, None, v[6], v[7], v[8]] for v in VK]
    for s in sorok:
        s += [None] * (len(fej) - len(s))

    def vk_kepletek():
        k = {}
        k[12] = lambda r: f"=IF(A{r}=\"\",\"\",IF(C{r}=\"eltérési engedély\",\"eltérési engedély\",IF(COUNTIF(F{r}:K{r},\"igen\")>0,\"jelentős\",\"kisebb\")))"
        k[13] = lambda r: f"=IF(L{r}=\"\",\"\",IF(L{r}=\"kisebb\",\"konfigurációs vezető\",\"konfigurációs bizottság\"))"
        k[17] = lambda r: (f"=IF(A{r}=\"\",\"\",IF(N{r}=\"elutasítva\",\"elutasítva\",IF(P{r}<>\"\",\"lezárt\","
                           f"IF(N{r}=\"jóváhagyva\",IF(C{r}=\"eltérési engedély\",\"érvényben\",\"végrehajtás alatt\"),\"döntésre vár\"))))")
        k[18] = lambda r: f"=IF(OR(E{r}=\"\",O{r}=\"\"),\"\",O{r}-E{r})"
        k[19] = lambda r: f"=IF(OR(E{r}=\"\",P{r}=\"\"),\"\",P{r}-E{r})"
        k[20] = lambda r: f"=IF(OR(Q{r}=\"\",Q{r}=\"lezárt\",Q{r}=\"elutasítva\"),\"\",'{O_LAP}'!$B$3-E{r})"
        k[21] = lambda r: f"=IF(A{r}=\"\",\"\",COUNTIF('{H_LAP}'!{oszl(r - R0)}${R0}:{oszl(r - R0)}${RU},\"x\"))"
        k[22] = lambda r: f"=IF(A{r}=\"\",\"\",COUNTIF('{H_LAP}'!{oszl(r - R0)}${B2}:{oszl(r - R0)}${B2 + NCI - 1},\"?\"))"
        k[23] = lambda r: (f"=IF(A{r}=\"\",\"\",IF(AND(Q{r}=\"lezárt\",V{r}>0),\"lezárva, de a hatáselemzés hiányos\","
                           f"IF(V{r}>0,\"egészítsd ki a hatáselemzést\",IF(AND(C{r}=\"változtatás\",U{r}=0),\"nincs módosítandó elem megjelölve\",\"\"))))")
        return k

    utv = tablazat(wv, R0 - 1, fej, [8, 44, 15, 18, 11] + [10] * 6 + [15, 21, 12, 11, 11, 15, 9, 9, 9, 11, 11, 30],
                   sorok, bemeneti_oszlopok=tuple(range(1, 12)) + (14, 15, 16), kepletek=vk_kepletek(),
                   uressor=NVK - len(VK), formatumok={5: "yyyy.mm.dd", 15: "yyyy.mm.dd", 16: "yyyy.mm.dd",
                                                       18: "0", 19: "0", 20: "0"})
    legordulo(wv, f"C{R0}:C{utv}", ["változtatás", "eltérési engedély"])
    legordulo(wv, f"F{R0}:K{utv}", ["igen", "nem"])
    legordulo(wv, f"N{R0}:N{utv}", ["jóváhagyva", "elutasítva", "függőben"])
    wv.conditional_formatting.add(f"F{R0}:K{utv}", CellIsRule(operator="equal", formula=['"igen"'], fill=NARANCS))
    wv.conditional_formatting.add(f"L{R0}:L{utv}", CellIsRule(operator="equal", formula=['"jelentős"'], font=Font(bold=True)))
    wv.conditional_formatting.add(f"W{R0}:W{utv}", FormulaRule(formula=[f'LEN(W{R0})>0'], fill=PIROS))
    wv.freeze_panes = f"C{R0}"
    V_UT = utv

    # ---- Hatásmátrix (CI × kérelem)
    wh = wb.create_sheet(H_LAP)
    cimsor(wh, "Hatásmátrix", "x: módosítandó elem; n: megvizsgálva, nem érinti. Az alsó blokk a még nem vizsgált, közvetlenül érintett elemeket jelzi.")
    wh.column_dimensions["A"].width, wh.column_dimensions["B"].width = 8, 34

    def blokk_fejlec(sor):
        fejlec(wh, sor, ["Az.", "Megnevezés"], [8, 34])
        for k in range(NVK):
            c = wh.cell(row=sor, column=3 + k)
            keplet(c, f"=IF('{V_LAP}'!A{R0 + k}=\"\",\"\",'{V_LAP}'!A{R0 + k})")
            c.font, c.fill, c.alignment = fej_font, fej_fill, Alignment(text_rotation=90, horizontal="center")
            wh.column_dimensions[oszl(k)].width = 4.6
        wh.row_dimensions[sor].height = 50

    blokk_fejlec(R0 - 1)
    for i in range(NCI):
        r = R0 + i
        keplet(wh.cell(row=r, column=1), f"=IF('{CI_LAP}'!A{r}=\"\",\"\",'{CI_LAP}'!A{r})")
        keplet(wh.cell(row=r, column=2), f"=IF('{CI_LAP}'!B{r}=\"\",\"\",'{CI_LAP}'!B{r})")
        for k in range(NVK):
            jel = VK[k][9].get(CI[i][0]) if (k < len(VK) and i < len(CI)) else None
            c = wh.cell(row=r, column=3 + k)
            bemenet(c, jel)
            c.alignment = kozep
    legordulo(wh, f"C{R0}:{oszl(NVK - 1)}{RU}", ["x", "n"])
    szoveg(wh.cell(row=30, column=2), "A kérelem állapota", felkov=True)
    for k in range(NVK):
        c = wh.cell(row=30, column=3 + k)
        keplet(c, f"=IF('{V_LAP}'!A{R0 + k}=\"\",\"\",'{V_LAP}'!Q{R0 + k})")
        c.alignment = Alignment(text_rotation=90, horizontal="center", vertical="bottom")
        c.font = Font(name="Arial", size=8)
    wh.row_dimensions[30].height = 70
    wh.conditional_formatting.add(f"C{R0}:{oszl(NVK - 1)}{RU}", CellIsRule(operator="equal", formula=['"x"'], fill=HALVANY))

    szoveg(wh.cell(row=B2 - 3, column=1), "Ellenőrizendő elemek: a módosítandó elemek közvetlen hatása alapján (?)", felkov=True)
    blokk_fejlec(B2 - 1)
    for i in range(NCI):
        r, rf = B2 + i, R0 + i
        keplet(wh.cell(row=r, column=1), f"=A{rf}")
        keplet(wh.cell(row=r, column=2), f"=B{rf}")
        kc = oszl(i)          # a Kapcsolatok lap i-edik oszlopa: mi hat az i-edik elemre
        for k in range(NVK):
            vc = oszl(k)
            f = (f"=IF(OR($A{r}=\"\",{vc}${R0 - 1}=\"\"),\"\",IF({vc}{rf}<>\"\",\"\","
                 f"IF(SUMPRODUCT(({vc}${R0}:{vc}${RU}=\"x\")*('{K_LAP}'!{kc}${R0}:{kc}${RU}=\"x\"))>0,\"?\",\"\")))")
            c = wh.cell(row=r, column=3 + k)
            keplet(c, f)
            c.alignment = kozep
    wh.conditional_formatting.add(f"C{B2}:{oszl(NVK - 1)}{B2 + NCI - 1}", CellIsRule(operator="equal", formula=['"?"'], fill=NARANCS))
    wh.freeze_panes = f"C{R0}"

    # ---- Összesítés
    wo = wb.create_sheet(O_LAP)
    cimsor(wo, "Összesítés")
    wo.column_dimensions["A"].width = 46
    szoveg(wo.cell(row=3, column=1), "Értékelés dátuma", felkov=True)
    bemenet(wo.cell(row=3, column=2), ERTEKELES, "yyyy.mm.dd")
    OSZT = ["jelentős", "kisebb", "eltérési engedély"]
    ALL = ["döntésre vár", "végrehajtás alatt", "érvényben", "lezárt", "elutasítva"]
    fejlec(wo, 5, ["Osztály"] + ALL + ["Összesen"], [46, 12, 12, 11, 10, 11, 10])
    L, Q = f"'{V_LAP}'!$L${R0}:$L${V_UT}", f"'{V_LAP}'!$Q${R0}:$Q${V_UT}"
    for i, o in enumerate(OSZT):
        r = 6 + i
        szoveg(wo.cell(row=r, column=1), o)
        for j, a in enumerate(ALL):
            keplet(wo.cell(row=r, column=2 + j), f'=COUNTIFS({L},$A{r},{Q},"{a}")', "0")
        keplet(wo.cell(row=r, column=7), f"=SUM(B{r}:F{r})", "0", True)
    rt = 6 + len(OSZT)
    szoveg(wo.cell(row=rt, column=1), "Összesen", felkov=True)
    for k in range(2, 8):
        cl = get_column_letter(k)
        keplet(wo.cell(row=rt, column=k), f"=SUM({cl}6:{cl}{rt - 1})", "0", True)

    V = f"'{V_LAP}'!"
    m0 = rt + 2
    mut = [
        ("Jelentős változások aránya a változtatásokon belül", f"=IFERROR(G6/(G6+G7),\"\")", "0%"),
        ("Átlagos idő a döntésig, jelentős (nap)", f"=IFERROR(AVERAGEIFS({V}R{R0}:R{V_UT},{L},\"jelentős\"),\"\")", "0.0"),
        ("Átlagos idő a döntésig, kisebb (nap)", f"=IFERROR(AVERAGEIFS({V}R{R0}:R{V_UT},{L},\"kisebb\"),\"\")", "0.0"),
        ("Átlagos átfutás a lezárásig, jelentős (nap)", f"=IFERROR(AVERAGEIFS({V}S{R0}:S{V_UT},{L},\"jelentős\"),\"\")", "0.0"),
        ("Átlagos átfutás a lezárásig, kisebb (nap)", f"=IFERROR(AVERAGEIFS({V}S{R0}:S{V_UT},{L},\"kisebb\"),\"\")", "0.0"),
        ("Legrégebben nyitott kérelem kora (nap)", f"=IF(COUNT({V}T{R0}:T{V_UT})=0,\"\",MAX({V}T{R0}:T{V_UT}))", "0"),
        ("Kiegészítendő hatáselemzések (db)", f"=COUNTIF({V}V{R0}:V{V_UT},\">0\")", "0"),
        ("Ellenőrizetlen elemek összesen (db)", f"=SUM({V}V{R0}:V{V_UT})", "0"),
        ("A legtöbb nyitott kérelem által érintett elem",
         f"=IF(MAX('{CI_LAP}'!I{R0}:I{RU})=0,\"–\",INDEX('{CI_LAP}'!B{R0}:B{RU},MATCH(MAX('{CI_LAP}'!I{R0}:I{RU}),'{CI_LAP}'!I{R0}:I{RU},0)))", None),
        ("A legtöbb elemre ható elem",
         f"=INDEX('{CI_LAP}'!B{R0}:B{RU},MATCH(MAX('{CI_LAP}'!J{R0}:J{RU}),'{CI_LAP}'!J{R0}:J{RU},0))", None),
    ]
    for i, (n, f, fm) in enumerate(mut):
        szoveg(wo.cell(row=m0 + i, column=1), n)
        keplet(wo.cell(row=m0 + i, column=2), f, fm, True)
        if fm is None:
            wo.merge_cells(start_row=m0 + i, start_column=2, end_row=m0 + i, end_column=6)

    ch = BarChart()
    ch.type, ch.grouping = "col", "clustered"
    diagram_kozos(ch, "Hatáselemzés kérelmenként", None, "elemek száma", 18, 8)
    s1 = Series(Reference(wv, min_col=21, min_row=R0, max_row=R0 + len(VK) - 1), title="módosítandó")
    s2 = Series(Reference(wv, min_col=22, min_row=R0, max_row=R0 + len(VK) - 1), title="ellenőrizetlen")
    ch.series.extend([s1, s2])
    ch.set_categories(Reference(wv, min_col=1, min_row=R0, max_row=R0 + len(VK) - 1))
    wo.add_chart(ch, "I3")
    return mentes(wb, "konfiguracio_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
