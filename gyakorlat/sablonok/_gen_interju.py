"""Interjúterv, interjúnapló és kódolási sablon (eszközlap: Interjú és megfigyelés)."""
from _kozos import *  # noqa: F401,F403

KATEG = ["funkció", "teljesítmény", "kezelhetőség", "megbízhatóság", "biztonság", "költség", "adat, információ", "egyéb"]

TERV = [
    ("Nyitás", "Bemutatkozás, az interjú célja, hozzájárulás a jegyzeteléshez", "–", "bizalom, keretek", 5),
    ("A mostani munka", "Meséljen el egy tipikus napot! Mivel kezdődik a műszak?", "Mi történik ezután? Ki ad munkát? Honnan tudja, mi a következő?", "a valós folyamat, nem a hivatalos", 10),
    ("Egy konkrét eset", "Gondoljon a legutóbbi alkalomra, amikor egy rendelés késett. Mi történt?", "Mikor derült ki? Ki tudott róla? Mit tett?", "konkrét történet, nem általánosítás", 10),
    ("Nehézségek", "Mi a legbosszantóbb a munkájában?", "Milyen gyakran fordul elő? Mennyi időt visz el? Mit csinál ilyenkor?", "problémák és megkerülő megoldások", 10),
    ("Kivételek", "Mi szokott váratlanul történni?", "Mi a legrosszabb, ami megtörtént? Hogyan oldották meg?", "rendellenes forgatókönyvek", 5),
    ("Elvárások", "Ha varázspálcája lenne, mit változtatna meg?", "Miért lenne ez jó? Mit nyerne vele?", "igények a kimondott megoldás mögött", 10),
    ("Prioritások", "Ha csak egy dolgot javíthatnánk, mi legyen az?", "Mi az, amiről semmiképp nem mondana le?", "fontossági sorrend", 5),
    ("Zárás", "Van valami, amit nem kérdeztem, de fontos?", "Kit javasol még megkérdezni?", "hiányzó témák, további érdekeltek", 5),
]

PELDA = [
    ("I-01", "Hétfőn megkapom a papírt, de szerdára már semmi sem igaz belőle.", "A gépkezelő a munka sorrendjének aktuális változását időben ismerje.", "adat, információ", "CNC-gépkezelő", 5),
    ("I-01", "Ha nincs anyag, elmegyek a raktárba, és ott derül ki, hogy nincs.", "A munka kiadásakor ismert legyen, hogy az anyag rendelkezésre áll-e.", "funkció", "CNC-gépkezelő", 5),
    ("I-01", "A beállítás néha egy óra, néha három, senki sem méri.", "A beállítási idők mérhetők és összevethetők legyenek.", "adat, információ", "CNC-gépkezelő", 4),
    ("I-02", "Tablet kell minden gép mellé.", "A gépnél, kézmosás nélkül is elérhető legyen a munkautasítás és a rajz.", "kezelhetőség", "CNC-gépkezelő", 4),
    ("I-02", "Olajos kézzel nem tudom nyomkodni a képernyőt.", "A gépnél használt kezelőfelület olajos, kesztyűs kézzel is működjön.", "kezelhetőség", "CNC-gépkezelő", 3),
    ("I-03", "Pénteken mindig túlórázunk, mert a vevő szólt, hogy sürgős.", "A sürgős rendelések hatása a többi határidőre előre látható legyen.", "funkció", "termelésvezető", 5),
    ("I-03", "Nem tudom, melyik gép mennyit áll.", "Gépenként ismert legyen a kihasználtság és az állásidő oka.", "adat, információ", "termelésvezető", 5),
    ("I-04", "Az audit előtt két napig keressük a papírokat.", "Egy munkadarab gyártási adatai néhány perc alatt visszakereshetők legyenek.", "adat, információ", "minőségügyi vezető", 4),
]


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Interjú és megfigyelés – sablon", [
        "■ Mire való? Az érdekelt felek elvárásainak feltárása félig strukturált interjúval, és a válaszok rendszerezése igényekké.",
        "1. Az „Interjúterv” lapon igazítsd a kérdéseket a saját projektedhez. A kérdések nyitottak, konkrét esetekre kérdeznek, és a megoldás helyett az igényt keresik.",
        "2. Az „Interjúnapló” lapon rögzítsd, kivel, mikor és milyen feltételekkel (hozzájárulás!) készült az interjú.",
        "3. A „Kódolás” lapon egy sor egy idézet vagy megfigyelés. Írd le szó szerint, majd fogalmazd át megoldásmentes igénnyé, és sorold kategóriába.",
        "4. Az „Összesítés” lap kategóriánként megszámolja az igényeket és átlagolja a fontosságot.",
        "■ Példa: a „Kódolás” lap a ForgácsTech négy interjújának kódolt részletét tartalmazza; írd felül a saját adataiddal.",
    ])
    ws = wb.create_sheet("Interjúterv")
    cimsor(ws, "Interjúterv (félig strukturált)", "60–75 perces interjúra; a sorrend rugalmas, a kérdések nyitottak.")
    tablazat(ws, 4, ["Téma", "Nyitó kérdés", "Mélyítő kérdések", "Mit akarunk megtudni?", "Idő (perc)"],
             [16, 44, 44, 28, 10], TERV, bemeneti_oszlopok=range(1, 6), uressor=4)
    r = 4 + len(TERV) + 4 + 1
    szoveg(ws.cell(row=r, column=4), "Összesen (perc):", felkov=True)
    keplet(ws.cell(row=r, column=5), f"=SUM(E5:E{r - 1})", felkov=True)

    ws = wb.create_sheet("Interjúnapló")
    cimsor(ws, "Interjúnapló")
    tablazat(ws, 4, ["Azonosító", "Interjúalany szerepe", "Dátum", "Helyszín (lehetőleg a munkahelyén)", "Interjúkészítő", "Jegyzetelő", "Hozzájárulás a jegyzeteléshez"],
             [11, 26, 12, 30, 18, 18, 16],
             [("I-01", "CNC-gépkezelő (megmunkáló központ)", "2026-03-02", "műhely, 3. gép mellett", "K. Anna", "T. Bence", "igen"),
              ("I-02", "CNC-gépkezelő (esztergák)", "2026-03-02", "műhely, pihenő", "K. Anna", "T. Bence", "igen"),
              ("I-03", "termelésvezető", "2026-03-03", "irodája", "K. Anna", "T. Bence", "igen"),
              ("I-04", "minőségügyi vezető", "2026-03-04", "minőségügyi labor", "K. Anna", "T. Bence", "igen")],
             bemeneti_oszlopok=range(1, 8), uressor=12, formatumok={3: "yyyy-mm-dd"})
    legordulo(ws, "G5:G30", ["igen", "nem"])

    ws = wb.create_sheet("Kódolás")
    cimsor(ws, "Idézetek és megfigyelések kódolása", "Az idézet szó szerinti; az igény megoldásmentes átfogalmazás.")
    u = tablazat(ws, 4, ["Interjú", "Idézet vagy megfigyelés (szó szerint)", "Igény (megoldásmentesen)", "Kategória", "Érdekelt fél", "Fontosság (1–5)"],
                 [10, 46, 46, 18, 20, 12], PELDA, bemeneti_oszlopok=range(1, 7), uressor=60)
    legordulo(ws, f"D5:D{u}", KATEG, "Kategória")
    megjegyzes(ws["C4"], "Tedd fel a kérdést: miért kell ez? A válasz az igény. Pl. „tablet minden gép mellé” → „a gépnél elérhető legyen a munkautasítás”.")
    ws.freeze_panes = "C5"

    ws = wb.create_sheet("Összesítés")
    cimsor(ws, "Összesítés kategóriánként")
    fejlec(ws, 4, ["Kategória", "Igények száma", "Átlagos fontosság"], [22, 14, 16])
    for i, k in enumerate(KATEG, start=5):
        szoveg(ws.cell(row=i, column=1), k)
        keplet(ws.cell(row=i, column=2), f"=COUNTIF(Kódolás!$D$5:$D${u},A{i})")
        keplet(ws.cell(row=i, column=3), f'=IFERROR(AVERAGEIF(Kódolás!$D$5:$D${u},A{i},Kódolás!$F$5:$F${u}),"")', "0.0")
    r = 5 + len(KATEG)
    szoveg(ws.cell(row=r, column=1), "Összesen", felkov=True)
    keplet(ws.cell(row=r, column=2), f"=SUM(B5:B{r - 1})", felkov=True)
    ch = BarChart()
    ch.type = "bar"
    ch.add_data(Reference(ws, min_col=2, min_row=4, max_row=r - 1), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=r - 1))
    diagram_kozos(ch, "Igények száma kategóriánként", None, "darab", 16, 8)
    ch.legend = None
    ws.add_chart(ch, "E4")
    return mentes(wb, "interju_sablon.xlsx")


if __name__ == "__main__":
    keszit()
