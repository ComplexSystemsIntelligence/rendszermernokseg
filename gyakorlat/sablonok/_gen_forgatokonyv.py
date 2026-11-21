"""Üzemmódok és működési forgatókönyvek sablonja (eszközlap: Működési koncepció és forgatókönyvek)."""
from _kozos import *  # noqa: F401,F403

JELLEG = ["névleges", "korlátozott", "rendellenes", "leromlott"]
TIPUS = ["normál", "rendellenes", "leromlott"]

MODOK = [
    ("UM-1", "kikapcsolt", "A cella feszültségmentes vagy energiatakarékos állapotban.", "műszak vége", "bekapcsolás", "névleges"),
    ("UM-2", "indítás, önteszt", "A vezérlés ellenőrzi a biztonsági köröket és a csavarozót.", "bekapcsolás", "önteszt rendben", "névleges"),
    ("UM-3", "normál üzem", "Az operátor és a kobot megosztva szereli a motort.", "önteszt rendben, hiba elhárítva", "hiba, vészleállítás, tervezett leállás", "névleges"),
    ("UM-4", "csökkentett sebesség", "Személy a védőzónában; a kobot lassít.", "kéz a védőzónában", "zóna szabad", "korlátozott"),
    ("UM-5", "leromlott üzem", "A kobot áll; az operátor kézzel szerel, nyomatékellenőrzéssel.", "robothiba", "hiba elhárítva", "leromlott"),
    ("UM-6", "vészleállítás", "Minden mozgás leáll; nyugtázás és ellenőrzés szükséges.", "vészgomb", "nyugtázás", "rendellenes"),
    ("UM-7", "karbantartás, típusváltás", "Tervezett leállás karbantartásra vagy átállásra.", "tervezett leállás", "átadás, próbaciklus", "névleges"),
]

FORG = [
    ("FK-01", "Egy motor szerelése", "normál", "UM-3", "operátor, kobot", "a befogó üres, alkatrész a tálcán",
     "1. Az operátor behelyezi a motorházat és a fedelet. 2. Nyugtázza a ciklusindítást. 3. A kobot pozicionálja a fedelet. 4. A csavarozó meghúzza a 8 csavart. 5. A kobot a kiadóba teszi a motort.",
     "a motor kész, nyomatékadatai a MES-ben", "R-01, R-03, R-07", 5, 2),
    ("FK-04", "Kéz a védőzónában ciklus közben", "rendellenes", "UM-4", "operátor, kobot", "a szenzor személyt érzékel",
     "1. A kobot sebessége csökken. 2. A jelzőlámpa sárgára vált. 3. A zóna kiürülése után a kobot folytatja.",
     "nincs ütközés, a ciklusidő legfeljebb 5 s-mal nő", "R-11, R-12", 4, 5),
    ("FK-09", "Nyomaték a tűrésen kívül", "rendellenes", "UM-3", "csavarozó, operátor", "egy csavar nyomatéka tűrésen kívül",
     "1. A csavarozó jelzi a hibát. 2. A cella a motort hibásként jelöli. 3. A kobot a hibás darabot a selejtdobozba teszi.",
     "hibás motor nem jut tovább", "R-07, R-08", 3, 4),
    ("FK-12", "Kifogy a csavaradagoló", "rendellenes", "UM-3", "operátor", "az adagoló üres",
     "1. A cella befejezi vagy félkészként jelöli a ciklust. 2. A kezelőpanel jelzi a hiányt. 3. Az operátor feltölt és nyugtáz.",
     "nincs nyomaték nélküli csavarkötés", "R-14", 4, 2),
    ("FK-15", "Robothiba két napig", "leromlott", "UM-5", "operátor, műszakvezető", "a kobot meghibásodik, szerviz 2 nap múlva",
     "1. A műszakvezető átállítja a cellát kézi üzemre. 2. Az operátor kézi csavarozóval, nyomatékellenőrzéssel szerel. 3. A MES csökkentett ütemmel tervez.",
     "legalább 60% teljesítmény, változatlan minőség", "R-21, R-22", 2, 4),
]


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Működési koncepció: üzemmódok és forgatókönyvek – sablon", [
        "■ Mire való? A jövőbeli rendszer használatának leírása a felhasználó nyelvén, normál, rendellenes és leromlott üzemben.",
        "1. Az „Üzemmódok” lapon sorold fel a rendszer üzemmódjait a be- és kilépési feltételekkel.",
        "2. A „Forgatókönyvek” lapon egy sor egy forgatókönyv azonosítóval, kiváltó eseménnyel, lépésekkel és elvárt eredménnyel. A lépések a felhasználó céljáról szóljanak, ne a kezelőfelület részleteiről.",
        "3. A valószínűség és a következmény (1–5) szorzata a forgatókönyv prioritása: a magas prioritásúakat dolgozd ki először és legrészletesebben.",
        "4. A „Lefedettség” lap üzemmódonként megszámolja a forgatókönyveket, és jelzi, ha egy üzemmódhoz nincs rendellenes forgatókönyv.",
        "■ Példa: a lapok a KoboCella üzemmódjait és öt forgatókönyvét tartalmazzák.",
    ])
    ws = wb.create_sheet("Üzemmódok")
    cimsor(ws, "Üzemmódok")
    u_m = tablazat(ws, 4, ["Kód", "Üzemmód", "Leírás", "Belépés feltétele", "Kilépés feltétele", "Jelleg"],
                   [9, 22, 44, 26, 30, 14], MODOK, bemeneti_oszlopok=range(1, 7), uressor=8)
    legordulo(ws, f"F5:F{u_m}", JELLEG)

    ws = wb.create_sheet("Forgatókönyvek")
    cimsor(ws, "Működési forgatókönyvek", "Valószínűség és következmény: 1 (kicsi) – 5 (nagy).")
    fej = ["Azonosító", "Cím", "Típus", "Üzemmód (kód)", "Szereplők", "Kiváltó esemény", "Lépések", "Elvárt eredmény",
           "Kapcsolódó követelmények", "Valószínűség (1–5)", "Következmény (1–5)", "Prioritás"]
    u_f = tablazat(ws, 4, fej, [10, 24, 12, 10, 18, 26, 60, 28, 16, 11, 11, 10], FORG,
                   bemeneti_oszlopok=range(1, 12),
                   kepletek={12: lambda r: f'=IF(OR(J{r}="",K{r}=""),"",J{r}*K{r})'}, uressor=20)
    legordulo(ws, f"C5:C{u_f}", TIPUS)
    for r in range(5, u_f + 1):
        ws.row_dimensions[r].height = 60 if r < 5 + len(FORG) else 18
    ws.freeze_panes = "C5"

    ws = wb.create_sheet("Lefedettség")
    cimsor(ws, "Lefedettség üzemmódonként")
    fejlec(ws, 4, ["Üzemmód (kód)", "Üzemmód", "normál", "rendellenes", "leromlott", "Ellenőrzés"], [14, 24, 10, 12, 11, 34])
    for i in range(u_m - 4):
        r = 5 + i
        keplet(ws.cell(row=r, column=1), f'=IF(Üzemmódok!A{5 + i}="","",Üzemmódok!A{5 + i})')
        keplet(ws.cell(row=r, column=2), f'=IF(Üzemmódok!B{5 + i}="","",Üzemmódok!B{5 + i})')
        for j, t in enumerate(TIPUS, start=3):
            keplet(ws.cell(row=r, column=j), f'=IF($A{r}="","",COUNTIFS(Forgatókönyvek!$D$5:$D${u_f},$A{r},Forgatókönyvek!$C$5:$C${u_f},"{t}"))')
        keplet(ws.cell(row=r, column=6), f'=IF(A{r}="","",IF(C{r}+D{r}+E{r}=0,"nincs forgatókönyv – kell-e?",IF(D{r}+E{r}=0,"nincs rendellenes forgatókönyv","rendben")))')
    return mentes(wb, "forgatokonyv_sablon.xlsx")


if __name__ == "__main__":
    keszit()
