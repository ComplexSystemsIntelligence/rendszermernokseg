"""Követelmény-nyomonkövetési mátrix (eszközlap: Nyomonkövethetőség)."""
from _kozos import *  # noqa: F401,F403

TIPUSOK = ["elvárás", "rendszerkövetelmény", "alrendszer-követelmény", "tervelem", "verifikáció"]
ELEMEK = [
    ("EF-01", "elvárás", "Évi 140 ezer motor összeszerelése (üzemigazgató)"),
    ("EF-03", "elvárás", "Ne kelljen hajolgatni és szerszámot tartani (operátorok)"),
    ("EF-07", "elvárás", "Minden motor nyomatékadatai visszakereshetők (vevő)"),
    ("R-01", "rendszerkövetelmény", "Ciklusidő legfeljebb 75 s"),
    ("R-02", "rendszerkövetelmény", "Havi rendelkezésre állás legalább 95%"),
    ("R-05", "rendszerkövetelmény", "Törzshajlítás legfeljebb 20°"),
    ("R-09", "rendszerkövetelmény", "Nyomatékadatok átadása a MES-nek a motor azonosítójával"),
    ("R-40", "rendszerkövetelmény", "A cella házán LED-es díszvilágítás (javaslat)"),
    ("CS-01", "alrendszer-követelmény", "Egy csavar meghúzása legfeljebb 3,2 s"),
    ("RB-01", "alrendszer-követelmény", "Kobot ki-be pakolási ciklusa legfeljebb 9 s"),
    ("MA-02", "alrendszer-követelmény", "Munkamagasság 950–1150 mm között állítható"),
    ("CS-04", "alrendszer-követelmény", "Minden meghúzás nyomatékának naplózása"),
    ("T-11", "tervelem", "Szervohajtású csavarorsó nyomaték- és szögméréssel"),
    ("T-12", "tervelem", "Motoros emelésű munkaasztal"),
    ("T-13", "tervelem", "Cellavezérlő OPC UA-kapcsolattal"),
    ("V-01", "verifikáció", "Ciklusidő-mérés 3 × 8 órás próbaüzemben"),
    ("V-09", "verifikáció", "Adatátadás bemutatása a MES tesztkörnyezetében"),
    ("V-14", "verifikáció", "Ergonómiai mérés és RULA-elemzés"),
]
KAPCS = [
    ("EF-01", "R-01"), ("EF-01", "R-02"), ("EF-03", "R-05"), ("EF-07", "R-09"),
    ("R-01", "CS-01"), ("R-01", "RB-01"), ("R-05", "MA-02"), ("R-09", "CS-04"),
    ("CS-01", "T-11"), ("CS-04", "T-11"), ("MA-02", "T-12"), ("CS-04", "T-13"),
    ("R-01", "V-01"), ("R-09", "V-09"), ("R-05", "V-14"), ("MA-02", "V-14"),
]


def lapok(wb, elo, adatok, kapcs, ures_e, ures_k):
    wk = wb.create_sheet(f"{elo}Kapcsolatok")
    cimsor(wk, "Kapcsolatok (szülő → gyerek)", "Egy sor egy nyomonkövetési kapcsolat: miből (szülő) mi lett (gyerek).")
    uk = tablazat(wk, 4, ["Szülő azonosító", "Gyerek azonosító", "Kapcsolat jellege"], [16, 16, 30],
                  [(a, b, "lebontás" if not b.startswith("V") else "verifikálja") for a, b in kapcs],
                  bemeneti_oszlopok=range(1, 4), uressor=ures_k)
    we = wb.create_sheet(f"{elo}Elemek")
    cimsor(we, "Elemek és ellenőrzés", "A szülők és gyerekek száma a „Kapcsolatok” lapból számolódik.")
    kl = f"'{elo}Kapcsolatok'"
    kep = {
        4: lambda r: f'=IF(A{r}="","",COUNTIF({kl}!$B$5:$B${uk},A{r}))',
        5: lambda r: f'=IF(A{r}="","",COUNTIF({kl}!$A$5:$A${uk},A{r}))',
        6: lambda r: (f'=IF(A{r}="","",TRIM(IF(AND(B{r}<>"elvárás",D{r}=0),"árva: nincs forrása (aranyozás?); ","")&'
                      f'IF(AND(OR(B{r}="elvárás",B{r}="rendszerkövetelmény",B{r}="alrendszer-követelmény"),E{r}=0),"nincs lebontva vagy verifikálva; ","")&'
                      f'IF(AND(B{r}="verifikáció",E{r}>0),"a verifikációnak nem lehet gyereke; ","")))'),
    }
    ue = tablazat(we, 4, ["Azonosító", "Típus", "Leírás", "Szülők száma", "Gyerekek száma", "Ellenőrzés"],
                  [12, 22, 50, 10, 10, 44], adatok, bemeneti_oszlopok=range(1, 4), kepletek=kep, uressor=ures_e)
    legordulo(we, f"B5:B{ue}", TIPUSOK)
    we.freeze_panes = "B5"
    return we, ue


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Követelmény-nyomonkövetési mátrix – sablon", [
        "■ Mire való? A kétirányú nyomonkövethetőség rögzítése és ellenőrzése: minden elvárásnak van-e követelménye, tervezési eleme és verifikációja, és minden elemnek van-e forrása.",
        "1. Az „Elemek” lapon sorold fel az elvárásokat, a rendszer- és alrendszer-követelményeket, a tervelemeket és a verifikációs tevékenységeket azonosítóval és típussal.",
        "2. A „Kapcsolatok” lapon egy sor egy kapcsolat: szülő → gyerek (például EF-01 → R-01, R-01 → CS-01, R-01 → V-01).",
        "3. Az „Ellenőrzés” oszlop jelzi az árva elemeket (nincs forrásuk) és a lebontatlan vagy verifikálatlan követelményeket.",
        "4. A követelmények verifikációs lefedettségét (van-e verifikáció a leszármazottak között) a nyomonkovetes.ipynb notebook ellenőrzi teljes körűen, és gráfként is felrajzolja a láncot.",
        "■ Példa: a „Példa –” lapok a KoboCella részletét tartalmazzák, benne egy szándékosan árva követelménnyel (R-40) és egy lebontatlannal (R-02).",
    ])
    lapok(wb, "", [], [], 80, 150)
    lapok(wb, "Példa – ", ELEMEK, KAPCS, 3, 5)
    # lapsorrend: Útmutató, Elemek, Kapcsolatok, Példa – Elemek, Példa – Kapcsolatok
    for nev, poz in [("Elemek", 1), ("Kapcsolatok", 2), ("Példa – Elemek", 3), ("Példa – Kapcsolatok", 4)]:
        wb.move_sheet(nev, offset=poz - wb.sheetnames.index(nev))
    return mentes(wb, "nyomonkovetes_sablon.xlsx")


if __name__ == "__main__":
    keszit()
