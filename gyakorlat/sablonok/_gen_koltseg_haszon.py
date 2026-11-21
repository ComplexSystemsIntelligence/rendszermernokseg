"""Költség–haszon elemzés jelenértéken, növekményes elemzéssel (eszközlap: Költség–haszon elemzés)."""
import json

from _kozos import *  # noqa: F401,F403

D = json.loads((MAPPA.parents[1] / "_shared" / "adat" / "kh_forgacs.json").read_text(encoding="utf-8"))
NA = 8


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Költség–haszon elemzés – sablon", [
        "■ Mire való? Egymást kizáró alternatívák összehasonlítása a várható hasznok és költségek jelenértékének arányával (B/C), nettó jelenértékkel és növekményes elemzéssel (Boardman és mtsai, 2018; Sullivan és mtsai, 2019).",
        "1. Az „Alternatívák” lapon add meg a kamatlábat és az időtávot (a rendszer várható élettartama).",
        "2. Alternatívánként add meg a beruházást, az éves működtetési költséget, az éves hasznot és a kockázati szorzót (0,5; 0,75 vagy 1 – finomabb megkülönböztetés nem indokolt). Minden összeg azonos pénznemben és egységben legyen.",
        "3. A lap kiszámolja a költségek és a (kockázattal korrigált) hasznok jelenértékét, a B/C arányt, a nettó jelenértéket és az egyszerű megtérülési időt.",
        "4. A „Növekményes” lap kizárja az 1-nél kisebb B/C arányú alternatívákat, a többit költség szerint sorba rendezi, és minden lépésben eldönti, megéri-e a drágább alternatíva többletköltsége (ΔB/ΔC > 1). A preferált alternatíva az utolsó elfogadott.",
        "5. A hasznok becslésének bizonytalanságát a koltseg_haszon notebook Monte Carlo-szimulációval vizsgálja.",
        "■ Példa: a ForgácsTech három MES-koncepciója (kézikönyv 10. fejezet).",
    ])
    ws = wb.create_sheet("Alternatívák")
    cimsor(ws, "Költség–haszon elemzés", D["megjegyzes"])
    szoveg(ws["A3"], "Kamatláb", felkov=True)
    bemenet(ws["B3"], D["kamatlab"], "0.0%")
    szoveg(ws["A4"], "Időtáv [év]", felkov=True)
    bemenet(ws["B4"], D["idotartam_ev"])
    szoveg(ws["C3"], "Annuitástényező", felkov=True)
    keplet(ws["D3"], "=(1-(1+B3)^(-B4))/B3", "0.0000")
    megjegyzes(ws["D3"], "Évente esedékes egységnyi összeg jelenértéke: Σ 1/(1+r)^t, t = 1…T.")
    fej = ["Kód", "Alternatíva", "Beruházás", "Éves működtetés", "Éves haszon", "Kockázati szorzó (f)",
           "Költségek jelenértéke (C)", "Hasznok jelenértéke (B)", "B/C", "Nettó jelenérték (B − C)", "Megtérülési idő [év]", "Megjegyzés"]
    sor = [[a["kod"], a["nev"], a["beruhazas"], a["eves_mukodtetes"], a["eves_haszon"], a["kockazati_szorzo"]] for a in D["alternativak"]]
    kepl = {7: lambda r: f'=IF(A{r}="","",C{r}+D{r}*$D$3)',
            8: lambda r: f'=IF(A{r}="","",E{r}*F{r}*$D$3)',
            9: lambda r: f'=IF(A{r}="","",H{r}/G{r})',
            10: lambda r: f'=IF(A{r}="","",H{r}-G{r})',
            11: lambda r: f'=IF(A{r}="","",IF(E{r}*F{r}-D{r}<=0,"nem térül meg",C{r}/(E{r}*F{r}-D{r})))',
            12: lambda r: f'=IF(A{r}="","",IF(I{r}<1,"B/C < 1: kiesik",""))'}
    u = tablazat(ws, 6, fej, [7, 30, 12, 13, 12, 12, 14, 14, 9, 14, 13, 18], sor, bemeneti_oszlopok=range(1, 7), kepletek=kepl,
                 uressor=NA - len(sor), formatumok={7: "0.0", 8: "0.0", 9: "0.00", 10: "0.0", 11: "0.0"})
    legordulo(ws, f"F7:F{u}", ["0.5", "0.75", "1"])
    # növekményes elemzés
    nv = wb.create_sheet("Növekményes")
    cimsor(nv, "Növekményes elemzés", "Csak a B/C ≥ 1 alternatívák, növekvő költség szerint; a védő (eddigi legjobb) és a kihívó összevetése.")
    fejlec(nv, 4, ["Sorrend", "Kihívó", "C", "B", "Védő (eddig preferált)", "ΔC", "ΔB", "ΔB/ΔC", "Megéri?", "Új védő"],
           [9, 10, 10, 10, 18, 10, 10, 10, 10, 10])
    # segédoszlop az Alternatívák lapon: rendezési kulcs
    keplet(ws.cell(row=6, column=14), "Rendezési kulcs (segéd)")
    for i in range(NA):
        r = 7 + i
        keplet(ws.cell(row=r, column=14), f'=IF(OR(A{r}="",I{r}=""),"",IF(I{r}>=1,G{r}+ROW()/1000000,""))', "0.000000")
    for k in range(NA):
        r = 5 + k
        keplet(nv.cell(row=r, column=1), f"={k + 1}")
        kul = f"Alternatívák!$N$7:$N${6 + NA}"
        keplet(nv.cell(row=r, column=2), f'=IFERROR(INDEX(Alternatívák!$A$7:$A${6 + NA},MATCH(SMALL({kul},A{r}),{kul},0)),"")')
        keplet(nv.cell(row=r, column=3), f'=IF(B{r}="","",INDEX(Alternatívák!$G$7:$G${6 + NA},MATCH(B{r},Alternatívák!$A$7:$A${6 + NA},0)))', "0.0")
        keplet(nv.cell(row=r, column=4), f'=IF(B{r}="","",INDEX(Alternatívák!$H$7:$H${6 + NA},MATCH(B{r},Alternatívák!$A$7:$A${6 + NA},0)))', "0.0")
        if k == 0:
            keplet(nv.cell(row=r, column=5), f'=IF(B{r}="","","–")')
            for c in (6, 7, 8):
                keplet(nv.cell(row=r, column=c), '=""')
            keplet(nv.cell(row=r, column=9), f'=IF(B{r}="","","(első)")')
            keplet(nv.cell(row=r, column=10), f'=B{r}')
        else:
            keplet(nv.cell(row=r, column=5), f'=IF(B{r}="","",J{r - 1})')
            cdef = f'INDEX(Alternatívák!$G$7:$G${6 + NA},MATCH(E{r},Alternatívák!$A$7:$A${6 + NA},0))'
            bdef = f'INDEX(Alternatívák!$H$7:$H${6 + NA},MATCH(E{r},Alternatívák!$A$7:$A${6 + NA},0))'
            keplet(nv.cell(row=r, column=6), f'=IF(B{r}="","",C{r}-{cdef})', "0.0")
            keplet(nv.cell(row=r, column=7), f'=IF(B{r}="","",D{r}-{bdef})', "0.0")
            keplet(nv.cell(row=r, column=8), f'=IF(B{r}="","",IF(F{r}=0,"",G{r}/F{r}))', "0.00")
            keplet(nv.cell(row=r, column=9), f'=IF(B{r}="","",IF(H{r}="","",IF(H{r}>1,"igen","nem")))')
            keplet(nv.cell(row=r, column=10), f'=IF(B{r}="",J{r - 1},IF(I{r}="igen",B{r},E{r}))')
    szoveg(nv.cell(row=7 + NA, column=1), "Preferált alternatíva", felkov=True)
    keplet(nv.cell(row=7 + NA, column=3), f"=J{4 + NA}", felkov=True)
    szoveg(nv.cell(row=8 + NA, column=1), "Legnagyobb B/C arányú", felkov=True)
    keplet(nv.cell(row=8 + NA, column=3), f'=INDEX(Alternatívák!$A$7:$A${6 + NA},MATCH(MAX(Alternatívák!$I$7:$I${6 + NA}),Alternatívák!$I$7:$I${6 + NA},0))')
    szoveg(nv.cell(row=9 + NA, column=1), "Legnagyobb nettó jelenértékű", felkov=True)
    keplet(nv.cell(row=9 + NA, column=3), f'=INDEX(Alternatívák!$A$7:$A${6 + NA},MATCH(MAX(Alternatívák!$J$7:$J${6 + NA}),Alternatívák!$J$7:$J${6 + NA},0))')
    megjegyzes(nv.cell(row=7 + NA, column=1), "Növekményes elemzés: a preferált alternatíva az utolsó, amelynek növekménye még megéri; nem feltétlenül a legnagyobb B/C arányú.")
    nv.column_dimensions["A"].width = 26
    return mentes(wb, "koltseg_haszon_sablon.xlsx")
