from _kozos import BETOLTO, code, fejresz, md

NEV = "qfd_minoseghaz"
CIM = "Minőségház (QFD): fontosság, érzékenység és közvetett hatások"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook egy minőségház adataiból

1. kiszámítja a műszaki jellemzők abszolút és relatív fontosságát;
2. hőtérképként ábrázolja a kapcsolati mátrixot;
3. **érzékenységvizsgálatot** végez: véletlenszerűen megzavarja a fontossági súlyokat és a kapcsolati erősségeket, és megnézi, mennyire stabil a rangsor;
4. a tetőmátrix figyelembevételével egyszerű **közvetett hatást** számít.

A beépített példa a kézikönyv VárosiBringa-minőségháza (7.3. szakasz).
""", sablon="qfd_sablon.xlsx", eszkozlap="Gyakorlati útmutató, QFD eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött qfd_sablon.xlsx „Minőségház” és „Tető” lapja
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("qfd_sablon.xlsx")
    h = pd.read_excel(fajl, sheet_name="Minőségház", header=None)
    jk = [v for v in h.iloc[3, 3:13] if isinstance(v, str)]
    m = len(jk)
    sorok = h.iloc[9:19, :3 + m].dropna(subset=[1])
    elvarasok = list(sorok[1]); w = sorok[2].astype(float).to_numpy()
    R = sorok.iloc[:, 3:3 + m].fillna(0).astype(float).to_numpy()
    jellemzok = [f"{k} {n}" for k, n in zip(jk, h.iloc[4, 3:3 + m])]
    t = pd.read_excel(fajl, sheet_name="Tető", header=None).iloc[4:4 + m, 1:1 + m]
    TERTEK = {"++": 1.0, "+": 0.5, "-": -0.5, "--": -1.0}
    C = np.array([[TERTEK.get(str(v).strip(), 0.0) for v in row] for row in t.to_numpy()])
    C = C + C.T
else:
    elvarasok = ["E1 elérhetőség", "E2 gyors kölcsönzés", "E3 megbízható zár", "E4 domb leküzdése",
                 "E5 megfizethető díj", "E6 biztonságos kerékpár"]
    w = np.array([5, 4, 4, 5, 3, 4], dtype=float)
    jellemzok = ["M1 állomássűrűség", "M2 kerékpár/állomás", "M3 kölcsönzési idő", "M4 hatótáv",
                 "M5 rásegítés", "M6 áthelyezés", "M7 zár ellenállása", "M8 tömeg", "M9 fékút"]
    R = np.array([[9, 9, 0, 3, 0, 9, 0, 0, 0],
                  [3, 0, 9, 0, 0, 0, 1, 0, 0],
                  [0, 0, 1, 0, 0, 0, 9, 0, 0],
                  [0, 0, 0, 9, 9, 0, 0, 3, 0],
                  [1, 3, 0, 0, 0, 3, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 3, 9]], dtype=float)
    C = np.zeros((9, 9))
    for a, b, v in [(0, 5, 0.5), (2, 6, -0.5), (3, 4, -0.5), (3, 7, -1.0), (4, 7, -0.5), (7, 8, 0.5)]:
        C[a, b] = C[b, a] = v
F = w @ R
eredmeny = pd.DataFrame({"abszolút": F, "relatív %": 100 * F / F.sum()}, index=jellemzok)
eredmeny["rang"] = eredmeny["abszolút"].rank(ascending=False, method="min").astype(int)
eredmeny.round(1).sort_values("rang")
'''),
    md("## A kapcsolati mátrix hőtérképe"),
    code('''
fig, ax = plt.subplots(figsize=(10, 4.2))
im = ax.imshow(R * w[:, None], cmap="Blues")
ax.set_xticks(range(len(jellemzok)), [j.split(" ", 1)[0] for j in jellemzok])
ax.set_yticks(range(len(elvarasok)), elvarasok)
for i in range(R.shape[0]):
    for j in range(R.shape[1]):
        if R[i, j]:
            ax.text(j, i, int(R[i, j]), ha="center", va="center", fontsize=9,
                    color="white" if R[i, j] * w[i] > 25 else "#1B3A57")
ax.set_title("Kapcsolati erősség × fontosság (a szám a kapcsolat erőssége)")
plt.colorbar(im, ax=ax, fraction=0.025); plt.tight_layout(); plt.show()
'''),
    md("""
## Érzékenységvizsgálat

A fontossági súlyok és a kapcsolati erősségek csapatbecslések. Megnézzük, mennyire stabil a rangsor, ha minden súlyt
±1-gyel, minden nem nulla kapcsolatot pedig egy fokozattal (9 ↔ 3 ↔ 1) véletlenszerűen elmozdítunk.
"""),
    code('''
rng = np.random.default_rng(42)
FOK = [1, 3, 9]
def zavar(R):
    Z = R.copy()
    for (i, j), v in np.ndenumerate(R):
        if v and rng.random() < 0.3:
            k = FOK.index(int(v)) + rng.choice([-1, 1])
            Z[i, j] = FOK[min(max(k, 0), 2)]
    return Z
N = 2000
rangok = np.zeros((N, len(jellemzok)), dtype=int)
for s in range(N):
    ws = np.clip(w + rng.integers(-1, 2, size=w.size), 1, 5)
    Fs = ws @ zavar(R)
    rangok[s] = (-Fs).argsort().argsort() + 1
stab = pd.DataFrame({"eredeti rang": eredmeny["rang"].to_numpy(),
                     "medián rang": np.median(rangok, axis=0),
                     "top-3 gyakoriság %": 100 * (rangok <= 3).mean(axis=0)}, index=jellemzok)
stab.sort_values("eredeti rang")
'''),
    md("""
## Közvetett hatások a tető alapján

Az egyszerű összegzés nem veszi figyelembe a tetőt. Egy egyszerű kiterjesztés: a $j$-edik jellemző korrigált
fontossága $F'_j = F_j + \\alpha \\sum_k C_{jk} F_k$, ahol $C$ a tető (támogató kapcsolat pozitív, gyengítő negatív),
$\\alpha$ pedig a közvetett hatás súlya. A pozitív korrekció azt jelzi, hogy a jellemző javítása más fontos jellemzőket
is segít; a negatív, hogy más fontos jellemzők rovására megy, ezért ott kompromisszum vagy innováció kell.
(A hipergráf- és hálózati folyam alapú QFD-ről lásd a kézikönyv 7.7. szakaszát.)
"""),
    code('''
ALFA = 0.3
Fk = F + ALFA * C @ F
kozvetett = pd.DataFrame({"egyszerű": F, "korrigált": Fk.round(1), "változás": (Fk - F).round(1)}, index=jellemzok)
display(kozvetett.sort_values("korrigált", ascending=False))
fig, ax = plt.subplots(figsize=(9, 3.6))
x = np.arange(len(jellemzok))
ax.bar(x - 0.2, F, 0.4, label="egyszerű", color="#A9C4DE")
ax.bar(x + 0.2, Fk, 0.4, label=f"tetővel korrigált (α = {ALFA})", color="#285780")
ax.set_xticks(x, [j.split(" ", 1)[0] for j in jellemzok]); ax.legend(); ax.set_ylabel("fontosság")
plt.tight_layout(); plt.savefig("qfd_fontossag.png", bbox_inches="tight"); plt.show()
'''),
    md("""
## Értelmezés

- A példában az **M1, M4** az első helyen áll; az érzékenységvizsgálat megmutatja, hogy a top-3 helyezésük mennyire biztos.
- A tetővel korrigált fontosság az **M4 (hatótáv)** és az **M8 (tömeg)** közötti erős ellentmondás miatt csökkenti mindkettőt: itt kompromisszumot (tömeghatár) vagy rendszerszintű megoldást (töltés a dokkolókban) kell keresni.
- Az $\\alpha$ értéke választás kérdése; érdemes több értékkel is kipróbálni.
"""),
]
