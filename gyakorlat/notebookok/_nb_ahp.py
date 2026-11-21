from _kozos import BETOLTO, code, fejresz, md

NEV = "ahp"
CIM = "Analitikus hierarchia eljárás (AHP): sajátvektor, következetesség, érzékenység"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. a páros összehasonlítási mátrixokból sajátvektor-módszerrel kiszámítja a súlyokat és a helyi prioritásokat, valamint a következetességi indexet (CI) és arányt (CR);
2. megkeresi a **legkövetkezetlenebb hármast**, vagyis azt a három elemet, amelynél az ítéletek a legjobban ellentmondanak egymásnak;
3. kiszámítja a globális prioritásokat, és megmutatja, hogyan változnak, ha a legfontosabb kritérium súlyát változtatjuk.

A beépített példa a ForgácsTech MES-koncepciójának kiválasztása (kézikönyv 10. fejezet).
""", sablon="ahp_sablon.xlsx", eszkozlap="Gyakorlati útmutató, AHP eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött ahp_sablon.xlsx
''' + BETOLTO + '''
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
RI = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
'''),
    md("## Adatok"),
    code('''
def blokk_olvasas(df, r0, kap):
    """Egy sablonblokk: r0 = a blokk címsora (0-alapú), utána fejléc, majd kap sor."""
    nevek = [v for v in df.iloc[r0 + 2:r0 + 2 + kap, 0] if isinstance(v, str)]
    n = len(nevek)
    M = df.iloc[r0 + 2:r0 + 2 + n, 1:1 + n].to_numpy(dtype=float)
    return nevek, M

if SAJAT_SABLON:
    fajl = sablon_betoltese("ahp_sablon.xlsx")
    k = pd.read_excel(fajl, sheet_name="Kritériumok", header=None)
    kriteriumok, K = blokk_olvasas(k, 2, 6)
    a = pd.read_excel(fajl, sheet_name="Alternatívák", header=None)
    alt_matrixok = {}
    for i, kn in enumerate(kriteriumok):
        alternativak, M = blokk_olvasas(a, 2 + 15 * i, 5)
        alt_matrixok[kn] = M
else:
    kriteriumok = ["K1 határidő-teljesítés", "K2 beruházási költség", "K3 bevezetési kockázat", "K4 bővíthetőség"]
    K = np.array([[1, 3, 3, 5], [1/3, 1, 1, 3], [1/3, 1, 1, 3], [1/5, 1/3, 1/3, 1]])
    alternativak = ["M1 teljes MES", "M2 gépgyártói + MES", "M3 fokozatos"]
    alt_matrixok = {
        kriteriumok[0]: np.array([[1, 3, 2], [1/3, 1, 1/2], [1/2, 2, 1]]),
        kriteriumok[1]: np.array([[1, 1/2, 1/4], [2, 1, 1/3], [4, 3, 1]]),
        kriteriumok[2]: np.array([[1, 3, 1/2], [1/3, 1, 1/4], [2, 4, 1]]),
        kriteriumok[3]: np.array([[1, 2, 4], [1/2, 1, 3], [1/4, 1/3, 1]])}
'''),
    md("## Súlyok és következetesség"),
    code('''
def ahp(M):
    sajat, vekt = np.linalg.eig(M)
    i = np.argmax(sajat.real)
    w = np.abs(vekt[:, i].real); w = w / w.sum()
    n = len(M); lam = sajat[i].real
    CI = (lam - n) / (n - 1) if n > 2 else 0.0
    CR = CI / RI[n] if n > 2 else 0.0
    g = np.prod(M, axis=1) ** (1 / n); g = g / g.sum()        # mértani közép (a sablon módszere)
    return w, g, lam, CI, CR

def legrosszabb_harmas(M, nevek):
    """Az a hármas, ahol a_ij · a_jk a legjobban eltér a_ik-tól (logaritmikus eltérés)."""
    if len(M) < 3:
        return None
    return max(((abs(np.log(M[i, j] * M[j, k] / M[i, k])), nevek[i], nevek[j], nevek[k])
                for i, j, k in itertools.combinations(range(len(M)), 3)), key=lambda t: t[0])

wK, gK, lamK, CIK, CRK = ahp(K)
print(f"Kritériumsúlyok (sajátvektor): {dict(zip(kriteriumok, wK.round(3)))}")
print(f"Kritériumsúlyok (mértani közép): {dict(zip(kriteriumok, gK.round(3)))}")
print(f"λmax = {lamK:.3f}, CI = {CIK:.3f}, CR = {CRK:.3f} -> {'elfogadható' if CRK <= 0.1 else 'VIZSGÁLD FELÜL'}")
h = legrosszabb_harmas(K, kriteriumok)
print(f"Legkövetkezetlenebb hármas: {h[1:]}, eltérés: {np.exp(h[0]):.2f}-szoros")

helyi = {}
for kn, M in alt_matrixok.items():
    w, g, lam, CI, CR = ahp(M)
    helyi[kn] = w
    print(f"{kn}: {dict(zip(alternativak, w.round(3)))}, CR = {CR:.3f}")
'''),
    md("## Globális prioritások és érzékenység"),
    code('''
L = np.column_stack([helyi[k] for k in kriteriumok])          # alternatívák × kritériumok
P = L @ wK
print("Globális prioritások:", dict(zip(alternativak, P.round(3))))

fig, axs = plt.subplots(1, 2, figsize=(12, 4))
bal = np.zeros(len(alternativak))
szin = ["#285780", "#E07B39", "#3E8E63", "#7D5BA6", "#B83A3A", "#999999"]
for k, kn in enumerate(kriteriumok):
    hozzajarulas = L[:, k] * wK[k]
    axs[0].barh(alternativak, hozzajarulas, left=bal, color=szin[k % 6], label=kn)
    bal += hozzajarulas
for i, v in enumerate(P):
    axs[0].text(v + 0.005, i, f"{v:.3f}", va="center", fontsize=9)
axs[0].invert_yaxis(); axs[0].legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2); axs[0].set_xlim(0, max(P) * 1.25)
axs[0].set_title("Globális prioritás kritériumonkénti hozzájárulással", fontsize=10)

racs = np.linspace(0, 0.9, 91)
gorbe = []
for w1 in racs:
    w = wK * (1 - w1) / (1 - wK[0]); w[0] = w1
    gorbe.append(L @ w)
gorbe = np.array(gorbe)
for j, a in enumerate(alternativak):
    axs[1].plot(racs, gorbe[:, j], color=szin[j], lw=2, label=a)
axs[1].axvline(wK[0], color="#999999", ls="--"); axs[1].text(wK[0] + 0.01, gorbe.min() + 0.01, "jelenlegi súly", fontsize=8)
axs[1].set_xlabel(f"{kriteriumok[0]} súlya"); axs[1].set_ylabel("globális prioritás"); axs[1].grid(alpha=0.3)
axs[1].legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3); axs[1].set_title("Érzékenység a legfontosabb kritérium súlyára", fontsize=10)
plt.tight_layout(); plt.savefig("ahp_prioritas.png", bbox_inches="tight", dpi=150); plt.show()

for j in range(1, len(alternativak)):
    d = gorbe[:, 0] - gorbe[:, j]
    valt = np.flatnonzero(np.diff(np.sign(d)))
    if len(valt):
        print(f"{alternativak[0]} és {alternativak[j]} sorrendje {racs[valt[0]]:.2f} körüli súlynál fordul meg.")
'''),
    md("""
## Értelmezés

- A ForgácsTech kritériummátrixa jól következetes (CR ≈ 0,016), az alternatívák mátrixai szintén 0,10 alatt vannak.
- A globális prioritás az M1-nél (0,417) és az M3-nál (0,401) csaknem azonos. A bal oldali ábra megmutatja, miért: az M1 a határidő-teljesítésből és a bővíthetőségből, az M3 a költségből és a kockázatból szerzi pontjait.
- Az érzékenységi görbe szerint az M1 és az M3 sorrendje a határidő-teljesítés súlyának kis csökkenésével megfordul. Ilyen szoros eredménynél az AHP nem dönt: más módszerrel (például költség–haszon elemzéssel) kell kiegészíteni, ahogy a kézikönyv esete is teszi.
- Ha egy mátrix CR-értéke 0,10 fölött van, kezdd a legkövetkezetlenebb hármas ítéleteinek felülvizsgálatával.
"""),
]
