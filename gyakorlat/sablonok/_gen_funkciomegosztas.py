"""Funkciómegosztás és automatizálási profil (eszközlap: Funkciómegosztás)."""
from _kozos import *  # noqa: F401,F403

FUNK = [  # id, funkció, seb, köv, ítélet, váratlan, költség, eset, megosztás, LOA (4), leromlott üzemben, indoklás
    ("1.1", "motorház befogása", "G", "G", "E", "E", "E", 2, "ember", (3, 1, 1, 1), "ember", "változatok kezelése, sérült alkatrész felismerése; a gépi befogás drága"),
    ("1.2", "fedél pozicionálása", "G", "G", "=", "E", "=", 3, "gép", (8, 7, 7, 8), "ember", "ismétlődő, pontos mozgás"),
    ("2.1", "csavar adagolása", "G", "G", "=", "=", "G", 5, "gép", (9, 8, 8, 9), "gép", "monoton, nagy darabszám"),
    ("2.2", "csavar meghúzása", "G", "G", "=", "E", "G", 3, "gép", (9, 7, 7, 8), "ember", "nyomatékpontosság, ergonómia"),
    ("2.3", "nyomaték mérése", "G", "G", "=", "=", "G", 5, "gép", (10, 9, 8, 9), "gép", "minden kötés adata kell (R-09)"),
    ("3.1", "adatok naplózása", "G", "G", "=", "=", "G", 5, "gép", (10, 10, 9, 10), "gép", "teljes, hibátlan adatrögzítés"),
    ("3.2", "hibás darab jelölése", "G", "G", "E", "E", "=", 1, "megosztott", (9, 8, 4, 2), "ember", "a gép jelez, az ember dönt a javításról vagy selejtezésről"),
    ("3.3", "adatátadás a MES-nek", "G", "G", "=", "=", "G", 5, "gép", (10, 10, 10, 10), "gép", "automatikus interfész"),
    ("4.1", "védőzóna figyelése", "G", "G", "=", "=", "=", 5, "gép", (10, 9, 10, 10), "gép", "biztonsági funkció, folyamatos figyelés"),
    ("4.2", "mozgás korlátozása", "G", "G", "=", "=", "=", 5, "gép", (10, 9, 10, 10), "gép", "biztonsági funkció, reakcióidő"),
    ("4.3", "vészleállítás", "G", "=", "E", "E", "=", 1, "megosztott", (9, 8, 7, 10), "ember", "automatikus és kézi indítás egyaránt"),
    ("5.1", "kész motor kivétele", "G", "G", "=", "=", "=", 3, "gép", (8, 7, 7, 8), "ember", "ergonómia, ciklusidő"),
    ("5.2", "elhelyezés a kiadóban", "G", "G", "=", "=", "=", 3, "gép", (8, 7, 7, 8), "ember", "ergonómia, ciklusidő"),
]
NF = 40


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Funkciómegosztás és automatizálási profil – sablon", [
        "■ Mire való? A funkciók megosztása ember, gép vagy együttes végrehajtás között, indoklással, és a döntés, a cselekvés automatizálási szintjének meghatározása a négy információfeldolgozási szakaszban.",
        "1. A „Megosztás” lapon soronként egy funkció (a funkciófa legalsó szintjéről). Öt szempontból jelöld, ki a jobb: G = gép, E = ember, = egyforma (Fitts-lista szellemében: sebesség, következetesség, ítélőképesség, váratlan helyzetek, költség).",
        "2. Válaszd ki Price megosztási esetét (1–6): 1 nincs különbség; 2 az ember jobb; 3 a gép jobb; 4 a gép túl gyenge → ember; 5 az ember túl gyenge → gép; 6 egyik sem elfogadható → újratervezés.",
        "3. Rögzítsd a döntést (ember / gép / megosztott) és az indoklást. A lap jelzi, ha a döntés ellentmond a jelöléseknek.",
        "4. Add meg az automatizálási szintet (1–10, Sheridan–Verplank) a négy szakaszra: információgyűjtés, információelemzés, döntés, végrehajtás (Parasuraman–Sheridan–Wickens).",
        "5. Rögzítsd, ki végzi a funkciót leromlott üzemben. Ha ott az ember, de normál üzemben a gép, a lap átvételi igényt jelez: ezt gyakoroltatni és a kezelőfelületen támogatni kell.",
        "■ Példa: a KoboCella funkcióinak megosztása (kézikönyv 12. fejezet).",
    ])
    ws = wb.create_sheet("Megosztás")
    cimsor(ws, "Funkciómegosztás", "G = gép jobb, E = ember jobb, = egyforma. Automatizálási szint: 1 (teljesen kézi) – 10 (teljesen automatikus).")
    fej = ["Azonosító", "Funkció", "Sebesség", "Következetesség", "Ítélőképesség", "Váratlan helyzetek", "Költség",
           "Gépi előny (db)", "Emberi előny (db)", "Megosztási eset (1–6)", "Döntés", "Jelzés",
           "LOA: információgyűjtés", "LOA: elemzés", "LOA: döntés", "LOA: végrehajtás", "Átlagos LOA",
           "Leromlott üzemben", "Átvételi igény", "Indoklás"]
    sor = [[a, b, c, d, e, f, g, None, None, h, i, None, *l, None, m, None, n] for a, b, c, d, e, f, g, h, i, l, m, n in FUNK]
    kepl = {8: lambda r: f'=IF(B{r}="","",COUNTIF(C{r}:G{r},"G"))',
            9: lambda r: f'=IF(B{r}="","",COUNTIF(C{r}:G{r},"E"))',
            12: lambda r: (f'=IF(OR(B{r}="",K{r}=""),"",IF(AND(K{r}="gép",I{r}>H{r}),"ellenőrizd: az ember több szempontból jobb",'
                           f'IF(AND(K{r}="ember",H{r}>I{r}+1),"ellenőrizd: a gép több szempontból jobb",IF(J{r}=6,"újratervezés szükséges",""))))'),
            17: lambda r: f'=IF(COUNT(M{r}:P{r})=0,"",AVERAGE(M{r}:P{r}))',
            19: lambda r: f'=IF(OR(B{r}="",R{r}=""),"",IF(AND(K{r}<>"ember",R{r}="ember"),"igen: gyakoroltatni kell",""))'}
    u = tablazat(ws, 4, fej, [9, 26, 9, 11, 10, 10, 8, 8, 8, 10, 11, 28, 10, 9, 9, 10, 9, 11, 20, 50], sor,
                 bemeneti_oszlopok=(1, 2, 3, 4, 5, 6, 7, 10, 11, 13, 14, 15, 16, 18, 20), kepletek=kepl,
                 uressor=NF - len(sor), formatumok={17: "0.0"})
    for r in range(5, u + 1):
        ws.cell(row=r, column=1).number_format = "@"
        for c in range(3, 18):
            ws.cell(row=r, column=c).alignment = kozep
    legordulo(ws, f"C5:G{u}", ["G", "E", "="])
    legordulo(ws, f"K5:K{u}", ["ember", "gép", "megosztott"])
    legordulo(ws, f"R5:R{u}", ["ember", "gép", "megosztott"])
    rr = u + 2
    for k_, (t, f, fmt) in enumerate([
            ("Funkciók: ember / gép / megosztott", f'=COUNTIF(K5:K{u},"ember")&" / "&COUNTIF(K5:K{u},"gép")&" / "&COUNTIF(K5:K{u},"megosztott")', None),
            ("Átlagos LOA: információgyűjtés", f"=IF(COUNT(M5:M{u})=0,\"\",AVERAGE(M5:M{u}))", "0.0"),
            ("Átlagos LOA: elemzés", f"=IF(COUNT(N5:N{u})=0,\"\",AVERAGE(N5:N{u}))", "0.0"),
            ("Átlagos LOA: döntés", f"=IF(COUNT(O5:O{u})=0,\"\",AVERAGE(O5:O{u}))", "0.0"),
            ("Átlagos LOA: végrehajtás", f"=IF(COUNT(P5:P{u})=0,\"\",AVERAGE(P5:P{u}))", "0.0"),
            ("Átvételi igények leromlott üzemben", f'=COUNTIF(S5:S{u},"igen*")', "0"),
            ("Ellentmondásjelzések", f'=COUNTIF(L5:L{u},"?*")', "0")]):
        szoveg(ws.cell(row=rr + k_, column=2), t, felkov=True)
        keplet(ws.cell(row=rr + k_, column=3), f, fmt, True)
        ws.merge_cells(start_row=rr + k_, start_column=3, end_row=rr + k_, end_column=5)
    ws.freeze_panes = "C5"
    lo = wb.create_sheet("LOA-skála")
    cimsor(lo, "Az automatizálás tíz szintje (Sheridan–Verplank)")
    tablazat(lo, 4, ["Szint", "Az automatika szerepe"], [8, 100], [
        [1, "a számítógép nem ad segítséget: mindenről az ember dönt, és ő cselekszik"],
        [2, "a számítógép a döntési vagy cselekvési alternatívák teljes körét felkínálja"],
        [3, "leszűkíti a választékot néhány lehetőségre"],
        [4, "egy alternatívát javasol"],
        [5, "végrehajtja a javaslatot, ha az ember jóváhagyja"],
        [6, "korlátozott ideig vétólehetőséget ad, majd automatikusan végrehajtja"],
        [7, "automatikusan végrehajtja, majd tájékoztatja az embert"],
        [8, "csak akkor tájékoztatja az embert, ha az kérdezi"],
        [9, "csak akkor tájékoztatja az embert, ha az automatika úgy dönt"],
        [10, "mindenről önállóan dönt és cselekszik, figyelmen kívül hagyja az embert"]])
    return mentes(wb, "funkciomegosztas_sablon.xlsx")
