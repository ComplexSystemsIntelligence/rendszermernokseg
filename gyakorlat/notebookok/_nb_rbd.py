from _kozos import BETOLTO, code, fejresz, md

NEV = "rbd"
CIM = "Megbízhatósági blokkdiagram: rendelkezésre állás, állásidő-hozzájárulás, Monte Carlo-ellenőrzés, k-ból-n"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. az elemek MTBF- és MTTR-adataiból kiszámítja a blokkok és a rendszer megbízhatóságát és rendelkezésre állását;
2. megmutatja, melyik elem mennyivel járul hozzá az éves állásidőhöz;
3. Monte Carlo-szimulációval (váltakozó működés–javítás) ellenőrzi az analitikus eredményt, és megmutatja az éves állásidő szórását;
4. egy $k$-ból-$n$ példán (a VárosiBringa dokkolóállomása) bemutatja, hogyan függ az állomás rendelkezésre állása a követelményként megadott $k$ értéktől.

A beépített példa a KoboCella termelési funkciója az UM-7 kézi tartalékkal (kézikönyv 16. fejezet).
""", sablon="rbd_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Megbízhatósági blokkdiagram eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött rbd_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import binom
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("rbd_sablon.xlsx")
    el = pd.read_excel(fajl, sheet_name="Elemek", header=4).iloc[:, :6]
    el.columns = ["id", "nev", "blokk", "MTBF", "MTTR", "forras"]
    el = el[el["id"].notna() & el["MTBF"].notna()]
    t_kuld = float(pd.read_excel(fajl, sheet_name="Elemek", header=None).iloc[2, 2])
    bl = pd.read_excel(fajl, sheet_name="Blokkok", header=3).iloc[:, :4]
    bl.columns = ["blokk", "nev", "tipus", "k"]
    bl = bl[bl["blokk"].notna() & bl["tipus"].notna()]
    rs = pd.read_excel(fajl, sheet_name="Rendszer", header=None)
    rendszer_tipus, H = str(rs.iloc[2, 2]), float(rs.iloc[7, 2])
else:
    el = pd.DataFrame({"id": ["E1", "E2", "E3", "E4", "E5", "E6"],
                       "nev": ["kobot", "csavarozó egység", "csavaradagoló", "lézerszkenner", "cellavezérlő", "UM-7 kézi tartalék"],
                       "blokk": ["B1"] * 5 + ["B2"], "MTBF": [8000, 2000, 1500, 20000, 30000, 490], "MTTR": [4, 1, 0.5, 2, 3, 10]})
    bl = pd.DataFrame({"blokk": ["B1", "B2"], "nev": ["KoboCella soros ága", "UM-7 kézi tartalék"], "tipus": ["soros", "soros"], "k": [None, None]})
    t_kuld, rendszer_tipus, H = 7.5, "párhuzamos", 3450
el["MTBF"] = el["MTBF"].astype(float); el["MTTR"] = el["MTTR"].astype(float)
el["A"] = el.MTBF / (el.MTBF + el.MTTR); el["R"] = np.exp(-t_kuld / el.MTBF)
el
'''),
    md("## Blokkok és rendszer"),
    code('''
def blokk_ertek(tipus, ertekek, k=None):
    ertekek = np.asarray(ertekek, float)
    if tipus == "soros":
        return ertekek.prod()
    if tipus == "párhuzamos":
        return 1 - (1 - ertekek).prod()
    n = len(ertekek); p = ertekek.mean()
    return binom.sf(int(k) - 1, n, p)          # P(legalább k működik)

eredm = []
for _, b in bl.iterrows():
    tag = el[el.blokk == b.blokk]
    eredm.append({"blokk": b.blokk, "nev": b.nev, "tipus": b.tipus, "R": blokk_ertek(b.tipus, tag.R, b.k), "A": blokk_ertek(b.tipus, tag.A, b.k)})
eredm = pd.DataFrame(eredm)
R_rsz = blokk_ertek(rendszer_tipus, eredm.R); A_rsz = blokk_ertek(rendszer_tipus, eredm.A)
print(eredm.to_string(index=False))
print(f"\\nRendszer ({rendszer_tipus}): R({t_kuld:g} h) = {R_rsz:.6f}, A = {A_rsz:.6f}, várható éves állásidő {(1 - A_rsz) * H:.2f} h")
b1 = el[el.blokk == eredm.blokk.iloc[0]]
lam = (1 / b1.MTBF).sum()
print(f"Az első blokk: λ = {lam:.3e} 1/h, MTBF = {1 / lam:.0f} h, évente {lam * H:.1f} meghibásodás, állásidő {(1 - eredm.A.iloc[0]) * H:.1f} h")
'''),
    md("## Monte Carlo-ellenőrzés az első blokkra"),
    code('''
rng = np.random.default_rng(7)
N = 3000
allasido = np.zeros(N)
for n in range(N):
    szakaszok = []
    for _, e in b1.iterrows():
        t = 0.0
        while t < H:
            t += rng.exponential(e.MTBF)
            if t >= H:
                break
            d = rng.exponential(e.MTTR)
            szakaszok.append((t, min(t + d, H)))
            t += d
    szakaszok.sort()
    ossz, veg = 0.0, -1.0
    for a, b in szakaszok:                      # az átfedő állások uniója (soros blokk)
        if b > veg:
            ossz += b - max(a, veg)
            veg = b
    allasido[n] = ossz
print(f"Szimulált éves állásidő: átlag {allasido.mean():.2f} h (analitikus {(1 - eredm.A.iloc[0]) * H:.2f} h), "
      f"90%-os tartomány {np.percentile(allasido, 5):.1f}–{np.percentile(allasido, 95):.1f} h")
'''),
    md("## Ábra"),
    code('''
fig, axs = plt.subplots(1, 3, figsize=(15, 4.3))
hozz = ((1 - b1.A) * H).to_numpy(); sorr = np.argsort(hozz)[::-1]
axs[0].barh(b1.nev.to_numpy()[sorr], hozz[sorr], color="#285780")
for i, v in enumerate(hozz[sorr]):
    axs[0].text(v + 0.03, i, f"{v:.2f} h", va="center", fontsize=8)
axs[0].invert_yaxis(); axs[0].set_xlabel("várható éves állásidő [h]"); axs[0].set_xlim(0, hozz.max() * 1.3)
axs[0].set_title("Az elemek hozzájárulása az állásidőhöz", fontsize=10)
axs[1].hist(allasido, bins=40, color="#7FA6CC", edgecolor="white")
axs[1].axvline((1 - eredm.A.iloc[0]) * H, color="#E07B39", lw=2, label="analitikus várható érték")
axs[1].set_xlabel("éves állásidő [h]"); axs[1].set_ylabel("szimulált évek száma"); axs[1].legend(fontsize=8)
axs[1].set_title("Monte Carlo: az éves állásidő eloszlása", fontsize=10)
n_dokk, A_dokk = 10, 0.98
ks = np.arange(1, n_dokk + 1)
axs[2].plot(ks, binom.sf(ks - 1, n_dokk, A_dokk), "o-", color="#3E8E63")
for k in (8, 10):
    v = binom.sf(k - 1, n_dokk, A_dokk)
    axs[2].annotate(f"k = {k}: {v:.3f}", (k, v), xytext=(k - 5.5, v - 0.06 * (11 - k)), fontsize=8, arrowprops=dict(arrowstyle="->", color="#999999"))
axs[2].set_xlabel("legalább ennyi dokkolónak kell működnie (k)"); axs[2].set_ylabel("az állomás rendelkezésre állása")
axs[2].set_ylim(0.75, 1.01); axs[2].grid(alpha=0.3); axs[2].set_title("k-ból-10: VárosiBringa-állomás (A = 0,98)", fontsize=10)
plt.tight_layout(); plt.savefig("rbd_elemzes.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A KoboCella soros ágának rendelkezésre állása 0,9985, ami évi mintegy 5 óra műszaki állásidő; ennek döntő része a kobottól és a csavarozó egységtől jön. A tartalék orsó (rövidebb MTTR) ezért a csavarozó egységnél a leghatékonyabb.
- A Monte Carlo-szimuláció átlaga egyezik az analitikus értékkel, de az egyes évek állásideje széles tartományban mozog: a tervezésnél és a szerződésekben a várható érték mellett a szórással is számolni kell.
- A $k$-ból-$n$ ábra szerint a „minden dokkoló működik” követelmény (k = 10) csak 0,82 valószínűséggel teljesül, a „legalább nyolc működik” 0,999-cel: a követelmény megfogalmazása legalább annyit számít, mint a hardver.
- A számítások független meghibásodást feltételeznek; közös okú hibáknál (közös táp, szoftver) a párhuzamos ág előnye kisebb.
"""),
]
