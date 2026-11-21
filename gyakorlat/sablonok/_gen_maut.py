"""Többszempontú hasznosságelemzés (MAUT): szakaszonként lineáris hasznossági függvények, ROC-súlyok."""
from _kozos import *  # noqa: F401,F403

KR = [  # kód, név, egység, rang, közvetlen súly, töréspontok (x, u)
    ("K1", "ciklusidő", "s", 2, 20, [(45, 10), (55, 9), (65, 7.5), (75, 4), (90, 0)]),
    ("K2", "utómunka-arány", "%", 1, 20, [(0.5, 10), (1.0, 8), (2.0, 4), (3.5, 0)]),
    ("K3", "legnagyobb törzshajlítás", "°", 3, 15, [(10, 10), (20, 7), (30, 2), (45, 0)]),
    ("K4", "beruházási költség", "MFt", 5, 15, [(0, 10), (60, 7), (90, 3), (120, 0)]),
    ("K5", "átállási idő", "perc", 4, 15, [(0, 10), (10, 7), (20, 3), (30, 0)]),
    ("K6", "technikai kockázat (pontszám a skáláról)", "pont", 6, 15, [(0, 0), (10, 10)]),
]
ALT = ["A: együttműködő cella", "B: fix állomás", "D: zárt robotcella"]
ERT = {"K1": [58.6, 52, 48], "K2": [0.8, 0.7, 0.6], "K3": [15, 15, 10], "K4": [78, 95, 110], "K5": [5, 30, 20], "K6": [6, 9, 2]}
NK, NA, NP = 8, 5, 5


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Többszempontú hasznosságelemzés (MAUT) – sablon", [
        "■ Mire való? Alternatívák értékelése nemlineáris hasznossági függvényekkel és többféle súlymeghatározással; a súlyozott értékelés továbbfejlesztése (Keeney–Raiffa, Edwards–Barron).",
        "1. A „Függvények” lapon kritériumonként legfeljebb öt töréspontot adhatsz meg (x növekvő sorrendben, hozzá a 0–10 hasznosság). A töréspontok között a lap lineárisan interpolál, a szélső pontokon túl a szélső értéket veszi.",
        "   A töréspontokat a döntéshozóval közösen határozd meg: „mennyit ér, ha a ciklusidő 65 s a 75 helyett?”. A követelmény határa körül gyakran meredek a függvény.",
        "2. A „Súlyok” lapon kétféle súlyozás közül választhatsz: közvetlen pontosztás (összesen 100) vagy rangsor-súlypont (ROC), amelyhez csak a kritériumok sorrendje kell.",
        "3. Az „Értékelés” lapon írd be az alternatívák értékeit. A lap kiszámolja a hasznosságokat, és mindkét súlyozással az összpontszámot és a rangsort.",
        "4. Ha a két súlyozás eltérő rangsort ad, a döntés a súlyok megválasztásán múlik: ezt a döntéshozóval tisztázni kell.",
        "5. Az additív modell akkor érvényes, ha a kritériumok preferenciafüggetlenek: két kritérium közötti átváltási hajlandóság nem függ a többi szintjétől.",
        "■ Példa: a KoboCella három koncepciója nemlineáris hasznossági függvényekkel.",
    ])
    fv = wb.create_sheet("Függvények")
    cimsor(fv, "Szakaszonként lineáris hasznossági függvények", "x értékek növekvő sorrendben; u: 0–10.")
    fej = ["Kód", "Kritérium", "Mértékegység"]
    for p in range(NP):
        fej += [f"x{p + 1}", f"u{p + 1}"]
    sor = []
    for k in KR:
        s = [k[0], k[1], k[2]]
        for p in range(NP):
            s += list(k[5][p]) if p < len(k[5]) else [None, None]
        sor.append(s)
    tablazat(fv, 4, fej, [7, 34, 12] + [8] * (2 * NP), sor, bemeneti_oszlopok=range(1, 4 + 2 * NP), uressor=NK - len(sor))
    sw = wb.create_sheet("Súlyok")
    cimsor(sw, "Súlyok", "Közvetlen: 100 pont szétosztása. ROC: w_i = (1/n)·Σ(k=r_i..n) 1/k, ahol r_i a kritérium rangja.")
    fejlec(sw, 4, ["Kód", "Kritérium", "Rang (1 = legfontosabb)", "Közvetlen súly", "Közvetlen súly (normált)", "ROC-súly"], [7, 34, 14, 12, 14, 12])
    for i in range(NK):
        r = 5 + i
        keplet(sw.cell(row=r, column=1), f'=IF(Függvények!A{r}="","",Függvények!A{r})')
        keplet(sw.cell(row=r, column=2), f'=IF(Függvények!B{r}="","",Függvények!B{r})')
        k = KR[i] if i < len(KR) else None
        bemenet(sw.cell(row=r, column=3), k[3] if k else None)
        bemenet(sw.cell(row=r, column=4), k[4] if k else None)
        keplet(sw.cell(row=r, column=5), f'=IF(OR(A{r}="",D{r}=""),"",D{r}/SUM($D$5:$D${4 + NK}))', "0.000")
        keplet(sw.cell(row=r, column=6), f'=IF(OR(A{r}="",C{r}=""),"",SUMIFS($J$5:$J$14,$I$5:$I$14,">="&C{r},$I$5:$I$14,"<="&$C${6 + NK})/$C${6 + NK})', "0.000")
    szoveg(sw.cell(row=6 + NK, column=2), "Kritériumok száma (n)", felkov=True)
    keplet(sw.cell(row=6 + NK, column=3), f'=COUNT(C5:C{4 + NK})')
    szoveg(sw.cell(row=7 + NK, column=2), "Súlyösszeg ellenőrzése (közvetlen / ROC)", felkov=True)
    keplet(sw.cell(row=7 + NK, column=5), f"=SUM(E5:E{4 + NK})", "0.000")
    keplet(sw.cell(row=7 + NK, column=6), f"=SUM(F5:F{4 + NK})", "0.000")
    fejlec(sw, 4, ["k", "1/k"], [6, 10], oszlop=9)
    for k in range(1, 11):
        keplet(sw.cell(row=4 + k, column=9), f"={k}")
        keplet(sw.cell(row=4 + k, column=10), f"=1/I{4 + k}", "0.000")
    ev = wb.create_sheet("Értékelés")
    cimsor(ev, "Értékelés", "Felső blokk: értékek (bemenet). Alsó blokk: hasznosság (0–10) interpolációval.")
    fejlec(ev, 4, ["Kód", "Kritérium"] + [""] * NA, [7, 34] + [18] * NA)
    for j in range(NA):
        bemenet(ev.cell(row=4, column=3 + j), ALT[j] if j < len(ALT) else None)
        ev.cell(row=4, column=3 + j).alignment = kozep
    for i in range(NK):
        r = 5 + i
        keplet(ev.cell(row=r, column=1), f'=IF(Függvények!A{r}="","",Függvények!A{r})')
        keplet(ev.cell(row=r, column=2), f'=IF(Függvények!B{r}="","",Függvények!B{r})')
        k = KR[i][0] if i < len(KR) else None
        for j in range(NA):
            bemenet(ev.cell(row=r, column=3 + j), ERT[k][j] if k and j < len(ERT[k]) else None)
            ev.cell(row=r, column=3 + j).alignment = kozep
    P0 = 7 + NK
    fejlec(ev, P0 - 1, ["Kód", "Hasznosság (0–10)"] + [""] * NA)
    for j in range(NA):
        col = get_column_letter(3 + j)
        keplet(ev.cell(row=P0 - 1, column=3 + j), f'=IF({col}4="","",{col}4)')
        ev.cell(row=P0 - 1, column=3 + j).fill, ev.cell(row=P0 - 1, column=3 + j).font = fej_fill, fej_font
    for i in range(NK):
        r = P0 + i
        fr = 5 + i
        keplet(ev.cell(row=r, column=1), f"=A{fr}")
        keplet(ev.cell(row=r, column=2), f"=B{fr}")
        X = [f"Függvények!${get_column_letter(4 + 2 * p)}${fr}" for p in range(NP)]
        U = [f"Függvények!${get_column_letter(5 + 2 * p)}${fr}" for p in range(NP)]
        for j in range(NA):
            col = get_column_letter(3 + j)
            x = f"{col}{fr}"
            # szakaszonként lineáris interpoláció: az utolsó kitöltött töréspontig
            belso = f"{U[NP - 1]}"
            for p in range(NP - 2, -1, -1):
                kov = f'IF({X[p + 1]}="",{U[p]},IF({x}<={X[p + 1]},{U[p]}+({U[p + 1]}-{U[p]})*({x}-{X[p]})/({X[p + 1]}-{X[p]}),{belso}))'
                belso = kov
            f = f'=IF(OR(${col}$4="",{x}="",{X[0]}=""),"",ROUND(IF({x}<={X[0]},{U[0]},{belso}),2))'
            keplet(ev.cell(row=r, column=3 + j), f, "0.00")
    rt = P0 + NK
    for k_, (t, wcol) in enumerate([("Összpontszám – közvetlen súlyok", "E"), ("Összpontszám – ROC-súlyok", "F")]):
        szoveg(ev.cell(row=rt + 2 * k_, column=2), t, felkov=True)
        szoveg(ev.cell(row=rt + 2 * k_ + 1, column=2), "Rang", felkov=False)
        for j in range(NA):
            col = get_column_letter(3 + j)
            keplet(ev.cell(row=rt + 2 * k_, column=3 + j),
                   f'=IF({col}$4="","",SUMPRODUCT(Súlyok!${wcol}$5:${wcol}${4 + NK},{col}{P0}:{col}{P0 + NK - 1}))', "0.00", True)
            keplet(ev.cell(row=rt + 2 * k_ + 1, column=3 + j),
                   f'=IF({col}$4="","",RANK({col}{rt + 2 * k_},$C${rt + 2 * k_}:${get_column_letter(2 + NA)}${rt + 2 * k_}))')
    return mentes(wb, "maut_sablon.xlsx")
