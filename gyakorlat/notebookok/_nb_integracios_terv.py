from _kozos import BETOLTO, code, fejresz, md

NEV = "integracios_terv"
CIM = "Integrációs terv: interfészjegyzék, N²-mátrix, a terv ellenőrzése és ütemezése"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. betölti a rendszer elemeit, interfészeit és az integrációs lépéseket;
2. ellenőrzi a tervet: minden interfész lépéshez van-e rendelve, nem korábbi-e a lépés, mint amikor mindkét eleme a rendszerben van, és jóváhagyott-e az interfészvezérlő dokumentum (ICD);
3. megrajzolja az N²-mátrixot, és kiszámolja az elemek kapcsolatszámát;
4. a kapcsolatok alapján integrációs sorrendet javasol, és összeveti a tervvel;
5. a lépések előzményeiből kritikus út módszerrel ütemez, megmutatja a kritikus utat és a tartalékokat, és megvizsgálja, mit okoz egy lépés csúszása.

A beépített példa a KoboCella integrációja (kézikönyv 22. fejezet; ISO/IEC/IEEE 15288:2023, 6.4.8.; Eppinger és Browning, 2012; Kelley és Walker, 1959; NASA SE Handbook, 5.2. szakasz és H függelék).
""", sablon="integracios_terv_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Integrációs terv és interfészmátrix eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött integracios_terv_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("integracios_terv_sablon.xlsx")
    el = pd.read_excel(fajl, sheet_name="Elemek", header=3).iloc[:15, :4]
    el.columns = ["elem", "tipus", "lepes", "felelos"]
    el = el[el.elem.notna()].reset_index(drop=True)
    it = pd.read_excel(fajl, sheet_name="Interfészek", header=3).iloc[:30, :11]
    it.columns = ["id", "a", "b", "irany", "tipus", "mi", "icd", "allapot", "felelos", "kockazat", "lepes"]
    it = it[it.id.notna() & it.a.notna() & it.b.notna()].reset_index(drop=True)
    lp = pd.read_excel(fajl, sheet_name="Lépések", header=3).iloc[:20, :14]
    lp = lp.iloc[:, [0, 1, 6, 8, 9, 10]]
    lp.columns = ["lepes", "nev", "teszt", "elozo1", "elozo2", "ido"]
    lp = lp[pd.to_numeric(lp.lepes, errors="coerce").notna()].reset_index(drop=True)
else:
    el = pd.DataFrame([
        ("Cellavezérlés (PLC)", 1), ("Biztonsági vezérlés", 1), ("Lézerszkenner", 1), ("Üzem (energia, környezet)", 1),
        ("Kobot", 2), ("Csavarozó orsó", 3), ("Csavaradagoló", 3), ("Csavarozó vezérlő", 3),
        ("Befogó készülék", 4), ("Motorház (munkadarab)", 4), ("Kezelőfelület (HMI)", 5), ("Kezelő", 5), ("MES", 6)],
        columns=["elem", "lepes"])
    it = pd.DataFrame([
        ("I-01", "Kobot", "Csavarozó orsó", "kétirányú", "mechanikai, energetikai, jel", "jóváhagyott", 3, 3),
        ("I-02", "Csavaradagoló", "Csavarozó orsó", "A→B", "mechanikai, pneumatikus", "jóváhagyott", 2, 3),
        ("I-03", "Kobot", "Cellavezérlés (PLC)", "kétirányú", "jel, adat", "jóváhagyott", 3, 2),
        ("I-04", "Lézerszkenner", "Biztonsági vezérlés", "A→B", "biztonsági jel", "jóváhagyott", 5, 1),
        ("I-05", "Befogó készülék", "Motorház (munkadarab)", "kétirányú", "mechanikai", "jóváhagyott", 3, 4),
        ("I-06", "Kezelő", "Kezelőfelület (HMI)", "kétirányú", "ember–gép", "jóváhagyott", 4, 5),
        ("I-07", "Csavarozó vezérlő", "MES", "A→B", "adat", "tervezet", 4, 6),
        ("I-08", "Üzem (energia, környezet)", "Cellavezérlés (PLC)", "A→B", "energetikai, környezeti", "jóváhagyott", 2, 1),
        ("I-09", "Biztonsági vezérlés", "Kobot", "A→B", "biztonsági jel", "jóváhagyott", 5, 2),
        ("I-10", "Biztonsági vezérlés", "Cellavezérlés (PLC)", "kétirányú", "jel", "jóváhagyott", 4, 1),
        ("I-11", "Csavarozó vezérlő", "Cellavezérlés (PLC)", "kétirányú", "jel, adat", "jóváhagyott", 3, 3),
        ("I-12", "Befogó készülék", "Cellavezérlés (PLC)", "A→B", "jel", "jóváhagyott", 2, 4),
        ("I-13", "Kezelőfelület (HMI)", "Cellavezérlés (PLC)", "kétirányú", "adat", "jóváhagyott", 3, 5),
        ("I-14", "Csavarozó vezérlő", "Csavarozó orsó", "kétirányú", "energetikai, jel", "jóváhagyott", 2, 3)],
        columns=["id", "a", "b", "irany", "tipus", "allapot", "kockazat", "lepes"])
    lp = pd.DataFrame([
        (1, "Vezérlés és biztonsági áramkör", "T1", None, None, 3), (2, "Kobot", "T2", 1, None, 3),
        (3, "Csavarozó orsó, adagoló, vezérlő", "T3", 2, None, 4), (4, "Befogó készülék, érzékelők", "T4", 3, None, 2),
        (5, "Kezelőfelület", "T5", 2, None, 3), (6, "MES-kapcsolat", "T6", 4, 5, 2),
        (7, "Gyári átvételi teszt (FAT)", "FAT", 6, None, 2), (8, "Bontás, szállítás, telepítés", "bekötés", 7, None, 4),
        (9, "Helyszíni átvételi teszt (SAT)", "SAT", 8, None, 3)],
        columns=["lepes", "nev", "teszt", "elozo1", "elozo2", "ido"])
for c in ("lepes", "kockazat"):
    it[c] = pd.to_numeric(it[c], errors="coerce")
el["lepes"] = pd.to_numeric(el["lepes"], errors="coerce")
lp[["lepes", "ido"]] = lp[["lepes", "ido"]].apply(pd.to_numeric, errors="coerce")
lp = lp[lp.lepes.notna()].copy(); lp["lepes"] = lp.lepes.astype(int)
print(f"{len(el)} elem, {len(it)} interfész, {len(lp)} lépés")
'''),
    md("""## A terv ellenőrzése

Minden interfészhez kell egy lépés, amelynek tesztje ellenőrzi. Ez a lépés nem lehet korábbi, mint az, amelyben az interfész mindkét eleme a rendszerbe kerül, és a lépés előtt az ICD-nek jóváhagyottnak kell lennie."""),
    code('''
lepes_of = dict(zip(el.elem, el.lepes))

def ellenoriz(s):
    if s.a not in lepes_of or s.b not in lepes_of:
        return "ismeretlen elem"
    if pd.isna(s.lepes):
        return "nincs lépéshez rendelve"
    if s.lepes < max(lepes_of[s.a], lepes_of[s.b]):
        return "túl korai lépés"
    if s.allapot != "jóváhagyott":
        return "ICD nincs jóváhagyva"
    return "rendben"

it["legkorabbi"] = [max(lepes_of.get(a, 0), lepes_of.get(b, 0)) for a, b in zip(it.a, it.b)]
it["ellenorzes"] = it.apply(ellenoriz, axis=1)
print(it[["id", "a", "b", "lepes", "legkorabbi", "allapot", "ellenorzes"]].to_string(index=False))
print(f"\\nLefedettség: {(it.ellenorzes == 'rendben').mean():.0%}")
for _, s in it[it.ellenorzes != "rendben"].iterrows():
    print(f"FIGYELEM: {s.id} ({s.a} – {s.b}): {s.ellenorzes}")
'''),
    md("""## N²-mátrix és kapcsolatszám

Az átlóban az elemek állnak; az *i*. sor és a *j*. oszlop kereszteződésében az *i*. elemtől a *j*. elemhez haladó interfészek. A sok kapcsolattal rendelkező elemre sok másik épül, ezért korai integrálása mellett szól, hogy a többi elem ellenőrzéséhez szükség van rá (Eppinger és Browning, 2012)."""),
    code('''
elemek = list(el.elem)
n = len(elemek); ix = {e: i for i, e in enumerate(elemek)}
N2 = np.zeros((n, n), dtype=int)
for _, s in it.iterrows():
    if s.a in ix and s.b in ix:
        if s.irany != "B→A":
            N2[ix[s.a], ix[s.b]] += 1
        if s.irany != "A→B":
            N2[ix[s.b], ix[s.a]] += 1
kapcsolat = pd.Series([len(set(it.loc[(it.a == e) | (it.b == e), "id"])) for e in elemek], index=elemek, name="interfész")
print(kapcsolat.sort_values(ascending=False).to_string())
'''),
    md("""## Integrációs sorrend a kapcsolatok alapján

Egyszerű mohó eljárás: a legtöbb kapcsolattal rendelkező elemmel kezdünk, és mindig azt az elemet vesszük hozzá, amelynek a legtöbb interfésze van a már integrált elemekkel (egyenlőségnél a kapcsolatszám dönt). Így minden lépésben ellenőrizhető interfészek keletkeznek, és a szabadon lógó, csak csonkkal tesztelhető elemek száma kicsi. Az eredmény javaslat: a tervet a kockázatok, az elemek elkészülésének sorrendje és a segédeszközök együtt határozzák meg (ISO/IEC/IEEE 15288:2023, 6.4.8.)."""),
    code('''
szomszed = {e: set() for e in elemek}
for _, s in it.iterrows():
    if s.a in szomszed and s.b in szomszed:
        szomszed[s.a].add(s.b); szomszed[s.b].add(s.a)
sorrend = [kapcsolat.idxmax()]
while len(sorrend) < n:
    maradek = [e for e in elemek if e not in sorrend]
    sorrend.append(max(maradek, key=lambda e: (len(szomszed[e] & set(sorrend)), kapcsolat[e])))
javaslat = pd.DataFrame({"elem": sorrend, "kapcsolat a már integráltakkal": [len(szomszed[e] & set(sorrend[:k])) for k, e in enumerate(sorrend)],
                         "a terv lépése": [lepes_of[e] for e in sorrend]})
print(javaslat.to_string(index=False))
'''),
    md("""## Ütemezés kritikus út módszerrel

A lépések előzményeiből a legkorábbi és a legkésőbbi kezdést, a tartalékot és a kritikus utat számoljuk (Kelley és Walker, 1959). A kritikus úton lévő lépés minden napnyi csúszása a teljes integrációt csúsztatja."""),
    code('''
lp = lp.sort_values("lepes").reset_index(drop=True)
elozok = {int(r.lepes): [int(x) for x in (r.elozo1, r.elozo2) if pd.notna(x) and str(x).strip() not in ("", "–")] for r in lp.itertuples()}
ido = dict(zip(lp.lepes.astype(int), lp.ido.astype(float)))

def cpm(ido):
    ES, EF = {}, {}
    for l in sorted(ido):
        ES[l] = max([EF[p] for p in elozok[l]], default=0.0); EF[l] = ES[l] + ido[l]
    T = max(EF.values())
    utod = {l: [k for k in ido if l in elozok[k]] for l in ido}
    LF, LS = {}, {}
    for l in sorted(ido, reverse=True):
        LF[l] = min([LS[k] for k in utod[l]], default=T); LS[l] = LF[l] - ido[l]
    return ES, EF, LS, LF, T

ES, EF, LS, LF, T = cpm(ido)
lp["kezdes"] = lp.lepes.map(ES); lp["befejezes"] = lp.lepes.map(EF)
lp["tartalek"] = [LS[l] - ES[l] for l in lp.lepes]
lp["interfesz"] = [int((it.lepes == l).sum()) for l in lp.lepes]
lp["kockazat"] = [int(it.loc[it.lepes == l, "kockazat"].sum()) for l in lp.lepes]
print(lp[["lepes", "nev", "ido", "kezdes", "befejezes", "tartalek", "interfesz", "kockazat"]].to_string(index=False))
print(f"\\nTeljes időtartam: {T:g} munkanap; kritikus út: {', '.join(str(l) for l in lp.lepes if abs(LS[l] - ES[l]) < 1e-9)}")
'''),
    md("""## Mit okoz egy lépés csúszása?

Ha egy lépés tesztje sikertelen, a lépést meg kell ismételni. A KoboCellánál a T6 teszt az I-07 interfész nyomatékadat-formátuma miatt bukott meg. A cella minden lépésnél egy napnyi ismétlést feltételezve kiszámolja a teljes időtartamot."""),
    code('''
for l in lp.lepes.astype(int):
    ido2 = dict(ido); ido2[l] += 1
    T2 = cpm(ido2)[4]
    print(f"{l}. lépés +1 nap → teljes időtartam {T2:g} nap ({'+' if T2 > T else ''}{T2 - T:g})")
egyszerre = int(it.lepes.notna().sum())
print(f"\\nEgyszerre integrálva egyetlen lépésben {egyszerre} interfészt kellene ellenőrizni; a tervben legfeljebb {lp.interfesz.max()} kerül egy lépésre.")
'''),
    md("## Ábra: N²-mátrix és integrációs ütemterv"),
    code('''
fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw={"width_ratios": [1, 1.25]})
rov = [e.split(" (")[0] for e in elemek]
a1.set_xlim(0, n); a1.set_ylim(n, 0); a1.set_aspect("equal")
for i in range(n):
    for j in range(n):
        if i == j:
            a1.add_patch(Rectangle((j, i), 1, 1, color="#285780"))
            a1.text(j + 0.5, i + 0.5, str(i + 1), ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        elif N2[i, j]:
            a1.add_patch(Rectangle((j, i), 1, 1, color="#F4D9A8"))
            a1.text(j + 0.5, i + 0.5, str(N2[i, j]), ha="center", va="center", color="#285780", fontsize=9)
        else:
            a1.add_patch(Rectangle((j, i), 1, 1, fill=False, ec="#E3E9EF", lw=0.6))
a1.set_xticks([]); a1.set_yticks(np.arange(n) + 0.5)
a1.set_yticklabels([f"{i + 1}. {r}" for i, r in enumerate(rov)], fontsize=8.5)
for s in a1.spines.values():
    s.set_visible(False)
a1.set_title("N²-mátrix (sor: kimenet, oszlop: bemenet)", fontsize=11)

kritikus = {l for l in lp.lepes if abs(LS[l] - ES[l]) < 1e-9}
for k, r in enumerate(lp.itertuples()):
    szin = "#285780" if r.lepes in kritikus else "#8FB0CF"
    a2.barh(k, r.ido, left=r.kezdes, color=szin, height=0.6)
    if r.interfesz:
        a2.text(r.befejezes + 0.25, k, f"{r.interfesz} interfész, kockázat {r.kockazat}", va="center", fontsize=8, color="#444")
a2.set_yticks(range(len(lp))); a2.set_yticklabels([f"{int(r.lepes)}. {r.nev}" for r in lp.itertuples()], fontsize=8.5)
a2.invert_yaxis(); a2.set_xlabel("munkanap"); a2.set_xlim(0, T + 7)
a2.grid(axis="x", alpha=0.3); a2.set_axisbelow(True)
a2.spines[["top", "right"]].set_visible(False)
a2.set_title(f"Integrációs ütemterv: {T:g} munkanap (sötét: kritikus út)", fontsize=11)
plt.tight_layout(); plt.savefig("integracios_terv.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""## Értelmezés

- Ha a terv lefedettsége 100%-nál kisebb, az integráció megkezdése előtt pótold a hiányt: rendeld lépéshez az interfészt, vagy hagyasd jóvá az ICD-t. A KoboCella tervében az I-07 ICD-je tervezet volt; éppen ez az interfész okozta a T6 teszt sikertelenségét.
- A kapcsolatszám és a mohó sorrend azt mutatja, mely elemekre épül a többi; a cellavezérlés korai integrálása ezért indokolt. A mohó eljárás csak a kapcsolatokat nézi: a lézerszkennert és az üzemi betáplálást a terv biztonsági okból veszi az első lépésbe, mert minden további lépés csak működő biztonsági funkciókkal végezhető biztonságosan.
- A kritikus úton lévő lépések ismétlése a teljes integrációt csúsztatja, a tartalékkal rendelkezőké nem: a kockázatos, kritikus úton lévő lépésekhez érdemes előre segédeszközt (szimulátort, tesztpéldányt) készíteni.
"""),
]
