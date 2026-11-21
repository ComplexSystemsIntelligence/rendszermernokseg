from _kozos import BETOLTO, code, fejresz, md

NEV = "gantt"
CIM = "Ütemezés és Gantt-diagram: sorolási elvek egy gépen, Johnson-eljárás két gépen, összevetés a teljes kereséssel"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. egy gépen összeveti az FCFS, SPT, EDD és CR sorolást (átlagos átfutás, késő feladatok, legnagyobb és teljes késedelem);
2. kis feladatszámnál teljes kereséssel ellenőrzi, hogy az SPT az átlagos átfutásra, az EDD a legnagyobb késedelemre optimális-e;
3. két egymást követő gépen Johnson eljárásával ütemez, és a teljes kereséssel igazolja az optimumot;
4. Gantt-diagramokat rajzol.

A beépített példa a ForgácsTech megmunkáló központja és 3D mérőgépe (kézikönyv 21. fejezet; Lakatos: Termelési rendszerek, 6.3; Johnson, 1954; Pinedo, 2022).
""", sablon="gantt_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Gantt-diagram és ütemezés eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött gantt_sablon.xlsx
''' + BETOLTO + '''
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("gantt_sablon.xlsx")
    e = pd.read_excel(fajl, sheet_name="Egy gép", header=7).iloc[:20, :4]   # a táblázat 20 sora
    e.columns = ["id", "p", "d", "sor"]
    egy = e[e.id.notna() & pd.to_numeric(e.p, errors="coerce").gt(0)].reset_index(drop=True)
    T0 = float(pd.read_excel(fajl, sheet_name="Egy gép", header=None, nrows=4).iloc[3, 1])
    k = pd.read_excel(fajl, sheet_name="Két gép (Johnson)", header=5).iloc[:15, :3]   # a táblázat 15 sora
    k.columns = ["id", "a", "b"]
    ket = k[k.id.notna() & pd.to_numeric(k.a, errors="coerce").notna() & pd.to_numeric(k.b, errors="coerce").notna()].reset_index(drop=True)
    ket = ket[~ket.id.astype(str).str.contains("csoport", case=False)]
else:
    egy = pd.DataFrame({"id": ["R1", "R2", "R3", "R4", "R5", "R6"], "p": [6, 2, 8, 3, 5, 4], "d": [20, 6, 30, 10, 12, 24], "sor": [1, 2, 3, 4, 5, 6]})
    ket = pd.DataFrame({"id": list("ABCDE"), "a": [4, 1, 5, 2, 3], "b": [2, 3, 4, 1, 5]})
    T0 = 0.0
for c in ("p", "d", "sor"):
    egy[c] = pd.to_numeric(egy[c], errors="coerce")
egy["sor"] = egy["sor"].fillna(pd.Series(range(1, len(egy) + 1)))
ket[["a", "b"]] = ket[["a", "b"]].astype(float)
print(egy.to_string(index=False)); print(ket.to_string(index=False))
'''),
    md("## Egy gép: sorolási elvek"),
    code('''
def mutatok(sorrend):
    t, befej = 0.0, {}
    for i in sorrend:
        t += egy.p[i]; befej[i] = t
    kes = {i: max(0.0, befej[i] - egy.d[i]) for i in sorrend}
    return dict(atlag=np.mean(list(befej.values())), keso=sum(v > 0 for v in kes.values()), maxkes=max(kes.values()),
                osszkes=sum(kes.values()), befej=befej)

idx = list(egy.index)
szabaly = {"FCFS": sorted(idx, key=lambda i: egy.sor[i]),
           "SPT": sorted(idx, key=lambda i: (egy.p[i], egy.sor[i])),
           "EDD": sorted(idx, key=lambda i: (egy.d[i], egy.sor[i])),
           "CR": sorted(idx, key=lambda i: ((egy.d[i] - T0) / egy.p[i], egy.sor[i]))}
eredm = {sz: mutatok(s) for sz, s in szabaly.items()}
tab = pd.DataFrame({sz: {"sorrend": ", ".join(egy.id[i] for i in szabaly[sz]), "átlagos átfutás": round(m["atlag"], 2),
                         "késő": m["keso"], "legnagyobb késedelem": m["maxkes"], "teljes késedelem": m["osszkes"]} for sz, m in eredm.items()}).T
print(tab.to_string())
if len(idx) <= 9:
    osszes = [mutatok(p) for p in itertools.permutations(idx)]
    print(f"Teljes keresés ({len(osszes)} sorrend): legkisebb átlagos átfutás {min(m['atlag'] for m in osszes):.2f}, "
          f"legkisebb legnagyobb késedelem {min(m['maxkes'] for m in osszes):.2f}, legkevesebb késő feladat {min(m['keso'] for m in osszes)}")
'''),
    md("## Két gép: Johnson-eljárás"),
    code('''
def johnson(df):
    elol = df[df.a <= df.b].sort_values("a")
    hatul = df[df.a > df.b].sort_values("b", ascending=False)
    return list(elol.index) + list(hatul.index)

def ket_gep(sorrend):
    t1 = t2 = 0.0; ut = []
    for i in sorrend:
        s1 = t1; t1 += ket.a[i]
        s2 = max(t1, t2); t2 = s2 + ket.b[i]
        ut.append((i, s1, t1, s2, t2))
    return t2, ut

J = johnson(ket)
Cj, ut_j = ket_gep(J)
Cf, ut_f = ket_gep(list(ket.index))
also = max(ket.a.sum() + ket.b.min(), ket.b.sum() + ket.a.min())
print(f"Johnson-sorrend: {', '.join(ket.id[i] for i in J)}; teljes átfutás {Cj:.1f} (érkezési sorrend: {Cf:.1f}; alsó korlát {also:.1f})")
if len(ket) <= 9:
    opt = min(ket_gep(p)[0] for p in itertools.permutations(ket.index))
    print(f"Teljes keresés: a legrövidebb teljes átfutás {opt:.1f} → a Johnson-sorrend {'optimális' if abs(opt - Cj) < 1e-9 else 'NEM optimális'}")
'''),
    md("## Ábra"),
    code('''
szinek = plt.cm.tab10.colors
fig, axs = plt.subplots(2, 1, figsize=(13, 7.5), gridspec_kw={"height_ratios": [1.3, 1]})
ax = axs[0]
for k, sz in enumerate(["FCFS", "SPT", "EDD"]):
    t = 0
    for i in szabaly[sz]:
        p = egy.p[i]; kes = eredm[sz]["befej"][i] > egy.d[i]
        ax.barh(k, p, left=t, color=szinek[i % 10], edgecolor="#B83A3A" if kes else "white", linewidth=2.5 if kes else 1)
        ax.text(t + p / 2, k, egy.id[i], ha="center", va="center", color="white", fontsize=9, weight="bold")
        t += p
    m = eredm[sz]
    ax.text(t + 0.5, k, f"átlag {m['atlag']:.1f}, késő {m['keso']}, max. késés {m['maxkes']:.0f}", va="center", fontsize=8.5)
for i in idx:
    ax.plot([egy.d[i]] * 2, [-0.5, 2.5], color=szinek[i % 10], ls=":", lw=1)
ax.set_yticks(range(3), ["FCFS", "SPT", "EDD"]); ax.invert_yaxis(); ax.set_xlabel("idő")
ax.set_title("Egy gép: sorolási elvek (piros keret: késő feladat; pontozott vonal: határidő)", fontsize=10)
ax.set_xlim(0, egy.p.sum() * 1.5)
ax = axs[1]
for k, (nev, ut, C) in enumerate([("érkezési sorrend", ut_f, Cf), ("Johnson-sorrend", ut_j, Cj)]):
    for i, s1, e1, s2, e2 in ut:
        y = 3 * k
        ax.barh(y, e1 - s1, left=s1, color=szinek[i % 10], edgecolor="white")
        ax.barh(y + 1, e2 - s2, left=s2, color=szinek[i % 10], edgecolor="white")
        ax.text((s1 + e1) / 2, y, ket.id[i], ha="center", va="center", color="white", fontsize=9, weight="bold")
        ax.text((s2 + e2) / 2, y + 1, ket.id[i], ha="center", va="center", color="white", fontsize=9, weight="bold")
    ax.text(C + 0.3, 3 * k + 0.5, f"{nev}: {C:.0f}", va="center", fontsize=9)
ax.set_yticks([0, 1, 3, 4], ["1. gép", "2. gép", "1. gép", "2. gép"]); ax.invert_yaxis(); ax.set_xlabel("idő")
ax.set_xlim(0, max(Cf, Cj) * 1.35)
ax.set_title("Két gép: érkezési sorrend (fent) és Johnson-sorrend (lent)", fontsize=10)
plt.tight_layout(); plt.savefig("gantt.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- Érkezési sorrendben négy rendelés késik, a legnagyobb késedelem 12 óra. Az SPT az átlagos átfutást csökkenti a legjobban (16,8 → 13,0 óra), az EDD-vel egyetlen rendelés sem késik. A teljes keresés igazolja, hogy egy gépen az SPT az átlagos átfutásra, az EDD a legnagyobb késedelemre optimális.
- A két gépes példában a Johnson-sorrend (B, E, C, A, D) 16 órára rövidíti a teljes átfutást az érkezési sorrend 20 órájáról; ez egyenlő az alsó korláttal, és a teljes keresés is ezt adja.
- A sorolási elvek egyszerűek és gyorsak, de egyetlen célt szolgálnak: ha a határidő-tartás és az átfutás egyaránt fontos, a kettő közötti kompromisszumot kell keresni (például EDD, az egyenlő határidejűek között SPT).
"""),
]
