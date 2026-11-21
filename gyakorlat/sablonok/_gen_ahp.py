"""Analitikus hierarchia eljárás (AHP): páros összehasonlítás, súlyok, következetesség, globális prioritás."""
import json

from _kozos import *  # noqa: F401,F403

D = json.loads((MAPPA.parents[1] / "_shared" / "adat" / "ahp_forgacs.json").read_text(encoding="utf-8"))
NK, NA = 6, 5
RI = [(1, 0), (2, 0), (3, 0.58), (4, 0.90), (5, 1.12), (6, 1.24), (7, 1.32), (8, 1.41), (9, 1.45), (10, 1.49)]


def matrix_blokk(ws, r0, cim, nevek, M, n_kap, ri_hely):
    """Páros összehasonlítási blokk: felső háromszög bemenet, alsó reciprok, súlyok, CR. Visszaadja a súlyoszlop címét és a következő szabad sort."""
    szoveg(ws.cell(row=r0, column=1), cim, felkov=True)
    hdr = r0 + 1
    fejlec(ws, hdr, ["Elem"] + [""] * n_kap + ["Mértani közép", "Súly", "(A·w)ᵢ", "(A·w)ᵢ / wᵢ"], [34] + [10] * n_kap + [12, 10, 10, 11])
    for j in range(n_kap):
        c = ws.cell(row=hdr, column=2 + j)
        keplet(c, f'=IF(A{hdr + 1 + j}="","",A{hdr + 1 + j})')
        c.fill, c.font, c.alignment = fej_fill, fej_font, kozep
    nn = f"COUNTIF($A${hdr + 1}:$A${hdr + n_kap},\"?*\")"
    for i in range(n_kap):
        r = hdr + 1 + i
        bemenet(ws.cell(row=r, column=1), nevek[i] if i < len(nevek) else None)
        for j in range(n_kap):
            c = ws.cell(row=r, column=2 + j)
            if i == j:
                keplet(c, f'=IF($A{r}="","",1)', "0.00")
            elif j > i:
                v = M[i][j] if i < len(M) and j < len(M) else None
                if v is not None and abs(v - round(v)) > 1e-9:
                    v = f"=1/{round(1 / v)}"
                bemenet(c, v, "0.00")
            else:
                src = f"{get_column_letter(2 + i)}{hdr + 1 + j}"
                keplet(c, f'=IF(OR($A{r}="",{get_column_letter(2 + j)}${hdr}="",{src}=""),"",1/{src})', "0.00")
            c.alignment = kozep
        last = get_column_letter(1 + n_kap)
        gm, w, aw, ratio = (get_column_letter(2 + n_kap + k) for k in range(4))
        keplet(ws.cell(row=r, column=2 + n_kap), f'=IF($A{r}="","",PRODUCT(B{r}:{last}{r})^(1/{nn}))', "0.000")
        keplet(ws.cell(row=r, column=3 + n_kap), f'=IF($A{r}="","",{gm}{r}/SUM(${gm}${hdr + 1}:${gm}${hdr + n_kap}))', "0.000")
    # súlyok sorvektorként a szorzathoz (segédsor)
    seg = hdr + n_kap + 1
    szoveg(ws.cell(row=seg, column=1), "súlyvektor (segédsor)")
    for j in range(n_kap):
        keplet(ws.cell(row=seg, column=2 + j), f'=IF(${w}{hdr + 1 + j}="",0,${w}{hdr + 1 + j})', "0.000")
    for i in range(n_kap):
        r = hdr + 1 + i
        keplet(ws.cell(row=r, column=4 + n_kap), f'=IF($A{r}="","",SUMPRODUCT(B{r}:{last}{r},$B${seg}:${last}${seg}))', "0.000")
        keplet(ws.cell(row=r, column=5 + n_kap), f'=IF($A{r}="","",{aw}{r}/{w}{r})', "0.000")
    s = seg + 1
    for k, (t, f, fmt) in enumerate([
            ("n (elemek száma)", f"={nn}", "0"),
            ("λmax (becslés)", f'=IF({nn}<1,"",AVERAGE({ratio}{hdr + 1}:{ratio}{hdr + n_kap}))', "0.000"),
            ("CI = (λmax − n)/(n − 1)", f'=IF({nn}<3,0,(B{s + 1}-B{s})/(B{s}-1))', "0.000"),
            ("RI (Saaty)", f"=IF(B{s}<3,0,VLOOKUP(B{s},{ri_hely},2,FALSE))", "0.00"),
            ("CR = CI/RI", f'=IF(B{s + 3}=0,0,B{s + 2}/B{s + 3})', "0.000"),
            ("Következetesség", f'=IF(B{s + 4}<=0.1,"elfogadható (CR ≤ 0,10)","vizsgáld felül az ítéleteket!")', None)]):
        szoveg(ws.cell(row=s + k, column=1), t, felkov=True)
        keplet(ws.cell(row=s + k, column=2), f, fmt)
    return w, hdr + 1, s + 7


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "AHP – sablon", [
        "■ Mire való? Kritériumsúlyok és alternatíva-prioritások meghatározása páros, szóbeli összehasonlításokból, a következetesség ellenőrzésével (Saaty).",
        "Saaty-skála: 1 = egyformán fontos, 3 = mérsékelten fontosabb, 5 = erősen fontosabb, 7 = nagyon erősen fontosabb, 9 = rendkívül fontosabb; 2, 4, 6, 8 = köztes. Ha a sor eleme a kevésbé fontos, a reciprokot írd (például 1/3).",
        "1. A „Kritériumok” lapon írd be a kritériumok nevét, és töltsd ki a mátrix felső háromszögét. Az alsó háromszög és az átló automatikus.",
        "2. A súlyokat a sorok mértani közepének normálásával számoljuk (a sajátvektor-módszer jó közelítése). A λmax becslése az (A·w)ᵢ/wᵢ hányadosok átlaga.",
        "3. Ha a CR nagyobb 0,10-nél, az ítéletek következetlenek: keresd meg az ellentmondó párokat (a notebook megmutatja), és vizsgáld felül őket.",
        "4. Az „Alternatívák” lapon kritériumonként hasonlítsd össze páronként az alternatívákat a kritérium szempontjából (költségnél és kockázatnál a kisebb a jobb!).",
        "5. Az „Eredmény” lap kiszámolja a globális prioritásokat: a kritériumsúlyokkal súlyozott helyi prioritások összegét.",
        "■ Példa: a ForgácsTech MES-koncepciójának kiválasztása (kézikönyv 10. fejezet).",
    ])
    ri = wb.create_sheet("RI")
    cimsor(ri, "Véletlen következetességi index (Saaty)")
    tablazat(ri, 4, ["n", "RI"], [8, 10], [list(x) for x in RI])
    ri_hely = "RI!$A$5:$B$14"
    kr = wb.create_sheet("Kritériumok")
    cimsor(kr, "A kritériumok páros összehasonlítása", f"Cél: {D['cel']}")
    wcol, wrow0, _ = matrix_blokk(kr, 3, "Kritériumok", D["kriteriumok"], D["kriterium_matrix"], NK, ri_hely)
    al = wb.create_sheet("Alternatívák")
    cimsor(al, "Az alternatívák páros összehasonlítása kritériumonként")
    r = 3
    helyi = []
    for k in range(NK):
        kn = D["kriteriumok"][k] if k < len(D["kriteriumok"]) else None
        M = D["alternativa_matrixok"].get(kn.split()[0]) if kn else None
        cim = f"Szempont: {kn}" if kn else f"{k + 1}. kritérium (üres)"
        w, r0, r = matrix_blokk(al, r, cim, D["alternativak"] if kn else [], M or [], NA, ri_hely)
        helyi.append((w, r0))
    er = wb.create_sheet("Eredmény")
    cimsor(er, "Globális prioritások", "Globális prioritás = Σ (kritériumsúly × helyi prioritás).")
    fejlec(er, 4, ["Alternatíva"] + [f"K{k + 1}" for k in range(NK)] + ["Globális prioritás", "Rang"], [34] + [10] * NK + [14, 8])
    szoveg(er.cell(row=5, column=1), "kritériumsúly", felkov=True)
    for k in range(NK):
        keplet(er.cell(row=5, column=2 + k), f'=IF(Kritériumok!{wcol}{wrow0 + k}="",0,Kritériumok!{wcol}{wrow0 + k})', "0.000")
    for a in range(NA):
        rr = 6 + a
        keplet(er.cell(row=rr, column=1), f'=IF(Alternatívák!A{helyi[0][1] + a}="","",Alternatívák!A{helyi[0][1] + a})')
        for k in range(NK):
            w, r0 = helyi[k]
            keplet(er.cell(row=rr, column=2 + k), f'=IF(OR($A{rr}="",Alternatívák!{w}{r0 + a}=""),"",Alternatívák!{w}{r0 + a})', "0.000")
        keplet(er.cell(row=rr, column=2 + NK), f'=IF($A{rr}="","",SUMPRODUCT($B$5:${get_column_letter(1 + NK)}$5,B{rr}:{get_column_letter(1 + NK)}{rr}))', "0.000", True)
        keplet(er.cell(row=rr, column=3 + NK), f'=IF($A{rr}="","",RANK({get_column_letter(2 + NK)}{rr},${get_column_letter(2 + NK)}$6:${get_column_letter(2 + NK)}${5 + NA}))')
    ch = BarChart()
    ch.type = "bar"
    ch.add_data(Reference(er, min_col=2 + NK, min_row=4, max_row=5 + len(D["alternativak"])), titles_from_data=True)
    ch.set_categories(Reference(er, min_col=1, min_row=6, max_row=5 + len(D["alternativak"])))
    diagram_kozos(ch, "Globális prioritások", None, "prioritás", 16, 7)
    ch.legend = None
    er.add_chart(ch, "A14")
    return mentes(wb, "ahp_sablon.xlsx")
