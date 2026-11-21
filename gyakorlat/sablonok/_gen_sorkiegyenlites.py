"""Ütemidő és sorkiegyenlítés (eszközlap: Ütemidő és sorkiegyenlítés)."""
from _kozos import *  # noqa: F401,F403

# azonosító, művelet, idő [s], típus, 1. megelőző, 2. megelőző, állomás, kezelő
MUVELETEK = [
    ("E1", "állórész behelyezése a készülékbe", 12, "kézi", None, None, 1, "K1"),
    ("E2", "tekercsvégek bekötése", 34, "kézi", "E1", None, 1, "K1"),
    ("E3", "csatlakozó beültetése", 24, "kézi", "E2", None, 1, "K1"),
    ("E4", "csapágy felsajtolása a rotorra", 20, "kézi", None, None, 2, "K2"),
    ("E5", "rotor behelyezése", 24, "kézi", "E3", "E4", 2, "K2"),
    ("E6", "hátsó pajzs felhelyezése", 18, "kézi", "E5", None, 2, "K2"),
    ("E7", "KoboCella: behelyezés, indítás", 18, "kézi", "E6", None, 3, "K3"),
    ("E8", "KoboCella: csavarozás és kivétel (kobot)", 56.1, "gépi", "E7", None, 3, None),
    ("E9", "tesztbe helyezés, csatlakoztatás", 12, "kézi", "E8", None, 4, "K4"),
    ("E10", "elektromos teszt (tesztberendezés)", 60, "gépi", "E9", None, 4, None),
    ("E11", "címkézés", 10, "kézi", "E10", None, 5, "K5"),
    ("E12", "csomagolás", 25, "kézi", "E11", None, 5, "K5"),
]
N = 30
NA = 8   # állomások
NK = 8   # kezelők


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Ütemidő és sorkiegyenlítés – sablon", [
        "■ Mire való? Egy szerelősor vagy ütemezett folyamat ütemidejének kiszámítása, a műveletek állomásokhoz és kezelőkhöz rendelése, az állomásidők ellenőrzése az ütemidővel, a kiegyenlítés hatásfoka és a Yamazumi-diagram (kézikönyv 19. fejezet; Scholl és Becker, 2006).",
        "1. A „Műveletek” lapon add meg a rendelkezésre álló időt és a keresletet ugyanarra az időszakra; a sablon kiszámítja az ütemidőt. Ha a berendezéshatékonyságra (OEE) tartalékot tervezel, add meg a tervezett OEE-t: a ciklusidő-korlát az ütemidő és az OEE szorzata.",
        "2. Soronként egy műveletelem: azonosító, megnevezés, idő másodpercben, típus (kézi vagy gépi), legfeljebb két közvetlen megelőző művelet azonosítója, a hozzárendelt állomás sorszáma és a kezelő azonosítója (gépi műveletnél üres).",
        "3. A „Sorrendi ellenőrzés” oszlop jelzi, ha egy művelet korábbi állomásra került, mint a megelőzője.",
        "4. Az „Állomások” lap állomásonként összesíti a kézi és a gépi időt, összeveti az ütemidővel és a korláttal, és kiszámítja az elméleti minimális állomásszámot, a kiegyenlítés hatásfokát és a sor kapacitását. A diagram a Yamazumi-diagram (halmozott oszlop: kézi és gépi idő; vonal: ütemidő és korlát).",
        "5. A „Kezelők” lap a kezelők kézi terhelését mutatja az ütemidőhöz képest. Gépi idő alatt a kezelő más műveletet is végezhet; az összevonás előtt az elrendezést és a terhelést (például NASA-TLX) is ellenőrizni kell.",
        "6. Próbálj ki más hozzárendelést: írd át az állomás- és kezelőoszlopot, és figyeld a mutatókat. Nagyobb feladatnál a sorkiegyenlites notebook heurisztikája javaslatot ad.",
        "■ Példa: a KoboCella ötállomásos motorszerelő sora (kézikönyv 19. fejezet).",
    ])
    ws = wb.create_sheet("Műveletek")
    cimsor(ws, "Ütemidő és műveletelemek")
    par = [("Rendelkezésre álló idő az időszakban [óra]", 3450, "#,##0"), ("Kereslet az időszakban [db]", 140000, "#,##0"),
           ("Tervezett berendezéshatékonyság (OEE)", 0.85, "0%")]
    for i, (t, v, fmt) in enumerate(par):
        szoveg(ws.cell(row=3 + i, column=1), t, felkov=True)
        bemenet(ws.cell(row=3 + i, column=2), v, fmt)
    szoveg(ws["A6"], "Ütemidő [s]", felkov=True)
    keplet(ws["B6"], '=IF(B4=0,"",B3*3600/B4)', "0.0", True)
    szoveg(ws["A7"], "Ciklusidő-korlát = ütemidő × OEE [s]", felkov=True)
    keplet(ws["B7"], '=IF(B6="","",B6*B5)', "0.0", True)
    fej = ["Azonosító", "Művelet", "Idő [s]", "Típus", "1. megelőző", "2. megelőző", "Állomás", "Kezelő", "Sorrendi ellenőrzés"]
    r1, rn = 10, 9 + N
    A, G = f"$A${r1}:$A${rn}", f"$G${r1}:$G${rn}"
    kepl = {9: lambda r: (f'=IF(A{r}="","",IF(OR(IFERROR(INDEX({G},MATCH(E{r},{A},0))>G{r},FALSE),'
                          f'IFERROR(INDEX({G},MATCH(F{r},{A},0))>G{r},FALSE)),"SÉRTI","rendben"))')}
    tablazat(ws, 9, fej, [11, 42, 9, 9, 11, 11, 9, 9, 14], [list(m) for m in MUVELETEK],
             bemeneti_oszlopok=(1, 2, 3, 4, 5, 6, 7, 8), kepletek=kepl, uressor=N - len(MUVELETEK),
             formatumok={3: "0.0", 7: "0"})
    legordulo(ws, f"D{r1}:D{rn}", ["kézi", "gépi"])
    M = "Műveletek!"
    C_, D_, G_, H_ = (f"{M}$C${r1}:$C${rn}", f"{M}$D${r1}:$D${rn}", f"{M}$G${r1}:$G${rn}", f"{M}$H${r1}:$H${rn}")

    a = wb.create_sheet("Állomások")
    cimsor(a, "Állomásidők és Yamazumi-diagram")
    fej = ["Állomás", "Kézi idő [s]", "Gépi idő [s]", "Állomásidő [s]", "Ütemidő [s]", "Ciklusidő-korlát [s]", "Az ütemidőn belül?", "A korláton belül?", "Tartalék a korlátig [s]"]
    fejlec(a, 3, fej, [10, 12, 12, 13, 12, 14, 13, 13, 14])
    for i in range(NA):
        r = 4 + i
        szoveg(a.cell(row=r, column=1), i + 1)
        keplet(a.cell(row=r, column=2), f'=SUMIFS({C_},{G_},A{r},{D_},"kézi")', "0.0")
        keplet(a.cell(row=r, column=3), f'=SUMIFS({C_},{G_},A{r},{D_},"gépi")', "0.0")
        keplet(a.cell(row=r, column=4), f"=SUMIF({G_},A{r},{C_})", "0.0", True)
        keplet(a.cell(row=r, column=5), f"={M}$B$6", "0.0")
        keplet(a.cell(row=r, column=6), f"={M}$B$7", "0.0")
        keplet(a.cell(row=r, column=7), f'=IF(D{r}=0,"",IF(D{r}<=E{r},"igen","NEM"))')
        keplet(a.cell(row=r, column=8), f'=IF(D{r}=0,"",IF(D{r}<=F{r},"igen","NEM"))')
        keplet(a.cell(row=r, column=9), f'=IF(D{r}=0,"",F{r}-D{r})', "0.0")
    ra = 4 + NA - 1
    r0 = ra + 2
    sor = [
        ("Munkatartalom [s]", f"=SUM({C_})", "0.0"),
        ("Használt állomások száma (N)", f'=COUNTIF(D4:D{ra},">0")', "0"),
        ("Legnagyobb állomásidő c [s]", f"=MAX(D4:D{ra})", "0.0"),
        ("Szűk keresztmetszet (állomás)", f'=IF(B{r0 + 2}=0,"",INDEX(A4:A{ra},MATCH(B{r0 + 2},D4:D{ra},0)))', "0"),
        ("Elméleti minimális állomásszám az ütemidőre", f'=IF({M}B6="","",ROUNDUP(B{r0}/{M}B6,0))', "0"),
        ("Elméleti minimális állomásszám a korlátra", f'=IF({M}B7="","",ROUNDUP(B{r0}/{M}B7,0))', "0"),
        ("A kiegyenlítés hatásfoka = munkatartalom / (N · c)", f'=IF(B{r0 + 1}*B{r0 + 2}=0,"",B{r0}/(B{r0 + 1}*B{r0 + 2}))', "0.0%"),
        ("A sor kapacitása [db/óra] = 3600 / c", f'=IF(B{r0 + 2}=0,"",3600/B{r0 + 2})', "0.0"),
        ("Igény [db/óra] = 3600 / ütemidő", f'=IF({M}B6="","",3600/{M}B6)', "0.0"),
        ("Sorrendi sértések száma", f'=COUNTIF({M}$I${r1}:$I${rn},"SÉRTI")', "0"),
        ("A korlátot túllépő állomások száma", f'=COUNTIF(H4:H{ra},"NEM")', "0"),
    ]
    for k, (t, f, fmt) in enumerate(sor):
        szoveg(a.cell(row=r0 + k, column=1), t)
        keplet(a.cell(row=r0 + k, column=2), f, fmt, True)
    a.column_dimensions["A"].width = 50
    ch = BarChart()
    ch.grouping = "stacked"; ch.overlap = 100
    ch.add_data(Reference(a, min_col=2, max_col=3, min_row=3, max_row=ra), titles_from_data=True)
    ch.set_categories(Reference(a, min_col=1, min_row=4, max_row=ra))
    lc = LineChart()
    lc.add_data(Reference(a, min_col=5, max_col=6, min_row=3, max_row=ra), titles_from_data=True)
    diagram_kozos(ch, "Yamazumi-diagram", "állomás", "idő [s]", 20, 9)
    ch += lc
    a.add_chart(ch, f"D{r0}")

    k = wb.create_sheet("Kezelők")
    cimsor(k, "A kezelők kézi terhelése")
    fejlec(k, 3, ["Kezelő", "Kézi munka [s/ütem]", "Ütemidő [s]", "Terhelés az ütemidőhöz", "Terhelés a korláthoz"], [10, 14, 12, 14, 14])
    for i in range(NK):
        r = 4 + i
        bemenet(k.cell(row=r, column=1), f"K{i + 1}")
        keplet(k.cell(row=r, column=2), f'=SUMIFS({C_},{H_},A{r},{D_},"kézi")', "0.0")
        keplet(k.cell(row=r, column=3), f"={M}$B$6", "0.0")
        keplet(k.cell(row=r, column=4), f'=IF(OR(B{r}=0,C{r}=""),"",B{r}/C{r})', "0%")
        keplet(k.cell(row=r, column=5), f'=IF(OR(B{r}=0,{M}$B$7=""),"",B{r}/{M}$B$7)', "0%")
    rk = 4 + NK - 1
    q0 = rk + 2
    for j, (t, f, fmt) in enumerate([
        ("Kezelők száma", f'=COUNTIF(B4:B{rk},">0")', "0"),
        ("Kézi munkatartalom [s]", f'=SUMIF({D_},"kézi",{C_})', "0.0"),
        ("A sor ciklusideje [s] = max(ütemidő, c)", f"=MAX({M}B6,Állomások!B{r0 + 2})", "0.0"),
        ("Átlagos munkaerő-kihasználtság", f'=IF(B{q0}=0,"",B{q0 + 1}/(B{q0}*B{q0 + 2}))', "0.0%"),
        ("Hozzá nem rendelt kézi művelet", f'=COUNTIFS({D_},"kézi",{H_},"")', "0"),
    ]):
        szoveg(k.cell(row=q0 + j, column=1), t)
        keplet(k.cell(row=q0 + j, column=2), f, fmt, True)
    k.column_dimensions["A"].width = 42
    szoveg(k.cell(row=q0 + 6, column=1), "Ha a sor keresletkorlátos (c < ütemidő), a sor az ütemidővel halad, és a kezelők ciklusideje az ütemidő.")
    return mentes(wb, "sorkiegyenlites_sablon.xlsx")


if __name__ == "__main__":
    print(keszit())
