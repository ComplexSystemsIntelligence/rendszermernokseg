from _kozos import BETOLTO, code, fejresz, md

NEV = "n2_dsm"
CIM = "Tervezési struktúramátrix (DSM): klaszterezés és modulok"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook egy komponensalapú, szimmetrikus DSM-ből

1. átlagos kapcsolású hierarchikus klaszterezéssel (a zárt szomszédsági halmazok Jaccard-távolsága alapján) modulokat javasol, és dendrogramot rajzol;
2. az eredeti és a klaszterezett sorrendben is kirajzolja a mátrixot, és megszámolja a modulokon belüli és a modulok közötti kapcsolatokat;
3. kiszámítja Newman modularitási mérőszámát (Q), és összeveti egy hálózattudományi közösségkereső algoritmus eredményével.

A beépített példa a VárosiBringa 12 elemű DSM-je (kézikönyv 8. fejezet).
""", sablon="n2_dsm_sablon.xlsx", eszkozlap="Gyakorlati útmutató, N²-diagram és DSM eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött n2_dsm_sablon.xlsx („Elemek” és „DSM” lap)
MODULOK_SZAMA = 3      # a dendrogram elvágásának helye
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from scipy.cluster.hierarchy import dendrogram, fcluster, leaves_list, linkage
from scipy.spatial.distance import squareform
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("n2_dsm_sablon.xlsx")
    el = pd.read_excel(fajl, sheet_name="Elemek", header=3).dropna(subset=["Kód"])
    kod, nev = list(el["Kód"].astype(str)), list(el["Elem neve"].astype(str))
    n = len(kod)
    M = pd.read_excel(fajl, sheet_name="DSM", header=None).iloc[4:4 + n, 1:1 + n].fillna(0).to_numpy(dtype=float)
    A = ((M + M.T) > 0).astype(int)
    np.fill_diagonal(A, 0)
else:
    kod = ["APP", "V", "D", "H", "A", "Z", "F", "TÖ", "M", "DV", "T", "ÁT"]
    nev = ["mobilalkalmazás", "váz és hajtás", "dokkoló mechanika", "háttérrendszer", "akkumulátor", "kerékpárzár",
           "fizetési modul", "töltőegység", "motor és vezérlő", "dokkolóvezérlő, kijelző", "fedélzeti telematika", "áthelyezés-tervező"]
    kapcsolatok = [("V", "A"), ("V", "M"), ("V", "Z"), ("V", "D"), ("A", "M"), ("A", "T"), ("A", "TÖ"), ("M", "T"),
                   ("Z", "T"), ("Z", "D"), ("T", "H"), ("D", "TÖ"), ("D", "DV"), ("TÖ", "DV"), ("DV", "H"),
                   ("H", "APP"), ("H", "F"), ("H", "ÁT"), ("APP", "F")]
    n = len(kod); I = {k: i for i, k in enumerate(kod)}
    A = np.zeros((n, n), int)
    for a, b in kapcsolatok:
        A[I[a], I[b]] = A[I[b], I[a]] = 1
print(f"{n} elem, {A.sum() // 2} kapcsolat, sűrűség: {A.sum() / (n * (n - 1)):.0%}")
'''),
    md("## Klaszterezés"),
    code('''
N = [set(np.flatnonzero(A[i])) | {i} for i in range(n)]           # zárt szomszédság
D = np.array([[1 - len(N[i] & N[j]) / len(N[i] | N[j]) for j in range(n)] for i in range(n)])
Z = linkage(squareform(D, checks=False), method="average")
cl = fcluster(Z, MODULOK_SZAMA, criterion="maxclust")
rend = list(leaves_list(Z))
belul = sum(A[i, j] for i in range(n) for j in range(i + 1, n) if cl[i] == cl[j])
kozott = A.sum() // 2 - belul
print("Klaszterezett sorrend:", [kod[i] for i in rend])
for c in sorted(set(cl)):
    print(f"  {c}. modul:", ", ".join(f"{kod[i]} ({nev[i]})" for i in rend if cl[i] == c))
print(f"Modulokon belül: {belul}, modulok között: {kozott} kapcsolat")
print("Modulinterfészek:", [(kod[i], kod[j]) for i in range(n) for j in range(i + 1, n) if A[i, j] and cl[i] != cl[j]])
'''),
    md("## Ábrák: eredeti és klaszterezett DSM, dendrogram"),
    code('''
szinek = ["#E07B39", "#3E8E63", "#7D5BA6", "#B83A3A", "#285780", "#999999"]
fig = plt.figure(figsize=(13, 4.8))
for k, (sorrend, cim) in enumerate([(list(range(n)), "eredeti sorrend"), (rend, "klaszterezett sorrend")]):
    ax = fig.add_subplot(1, 3, k + 1)
    B = A[np.ix_(sorrend, sorrend)].astype(float)
    np.fill_diagonal(B, 2)
    ax.imshow(B, cmap="Blues", vmin=0, vmax=2.2)
    ax.set_xticks(range(n), [kod[i] for i in sorrend], rotation=90, fontsize=8)
    ax.set_yticks(range(n), [kod[i] for i in sorrend], fontsize=8)
    ax.set_title(cim, fontsize=10)
    if k == 1:
        p = 0
        for s, c in enumerate(dict.fromkeys(cl[i] for i in rend)):
            m = sum(1 for i in rend if cl[i] == c)
            ax.add_patch(plt.Rectangle((p - 0.5, p - 0.5), m, m, fill=False, ec=szinek[s % 6], lw=2.2))
            p += m
ax = fig.add_subplot(1, 3, 3)
dendrogram(Z, labels=kod, ax=ax, color_threshold=Z[-(MODULOK_SZAMA - 1), 2] - 1e-9, above_threshold_color="#999999")
ax.set_title("dendrogram (átlagos kapcsolás, Jaccard-távolság)", fontsize=10); ax.tick_params(labelsize=8)
plt.tight_layout(); plt.savefig("dsm_klaszter.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("## Newman-modularitás és összevetés közösségkereséssel"),
    code('''
G = nx.from_numpy_array(A)
klaszter_halmazok = [set(np.flatnonzero(cl == c)) for c in sorted(set(cl))]
Q_klaszter = nx.algorithms.community.modularity(G, klaszter_halmazok)
kozossegek = nx.algorithms.community.greedy_modularity_communities(G)
Q_kozosseg = nx.algorithms.community.modularity(G, kozossegek)
print(f"Hierarchikus klaszterezés: Q = {Q_klaszter:.3f}")
print(f"Mohó modularitás-maximalizálás: Q = {Q_kozosseg:.3f}, {len(kozossegek)} közösség:")
for c in kozossegek:
    print("  ", sorted(kod[i] for i in c))
'''),
    md("""
## Értelmezés

- A klaszterezett mátrixban a keretezett blokkok a javasolt modulok; a blokkokon kívüli kapcsolatok a **modulinterfészek**, amelyekhez interfészgazdát és interfészdokumentációt kell rendelni.
- A Newman-féle Q azt méri, mennyivel több kapcsolat esik a modulokon belülre, mint véletlenszerű kapcsolódásnál. A 0,3 fölötti érték már határozott modulszerkezetre utal; a különböző algoritmusok eredményét ezzel lehet összevetni.
- Az algoritmus javaslat, nem döntés: a modulhatárok kijelölésénél a beszállítói csomagok, a szervezeti felelősségek és a jövőbeli változások is számítanak (kézikönyv 8.7. szakasz).
- Próbáld ki: állítsd a `MODULOK_SZAMA` értékét 2-re vagy 4-re, és figyeld, hogyan változnak a modulok és a modulinterfészek!
"""),
]
