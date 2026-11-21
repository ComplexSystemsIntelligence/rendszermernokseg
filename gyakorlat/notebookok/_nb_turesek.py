from _kozos import BETOLTO, code, fejresz, md

NEV = "turesek"
CIM = "Tűréslánc: legrosszabb eset, RSS és Monte Carlo, szóráshozzájárulás, a középérték-eltolódás hatása"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. a tűrésláncot legrosszabb esetre és négyzetes összegzéssel (RSS) számítja;
2. Monte Carlo-szimulációval ellenőrzi az eredményt a tagok tényleges eloszlásával (normális vagy egyenletes) és középérték-eltolódással;
3. megmutatja, melyik tag mekkora részben felel az eredő szórásért;
4. megvizsgálja, mekkora középérték-eltolódás fér bele a követelménybe egy kiválasztott tagnál.

A beépített példa a KoboCella fedéltömítésének összenyomódása (kézikönyv 18. fejezet; Chase és Parkinson, 1991).
""", sablon="turesek_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Tűréslánc eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött turesek_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("turesek_sablon.xlsx")
    l = pd.read_excel(fajl, sheet_name="Lánc", header=3).iloc[:, :6]
    l.columns = ["tag", "nevleges", "tur", "a", "eloszlas", "eltolas"]
    lanc = l[l["tag"].notna() & l["nevleges"].notna()].reset_index(drop=True)
    e = pd.read_excel(fajl, sheet_name="Eredmény", header=None)
    LSL, USL, SZINT = float(e.iloc[3, 2]), float(e.iloc[4, 2]), float(e.iloc[5, 2])
else:
    lanc = pd.DataFrame({"tag": ["tömítés vastagsága", "fedél horonymélysége", "motorház tömítőperem", "fedél síklapúsága"],
                         "nevleges": [2.50, 2.20, 0.30, 0.00], "tur": [0.08, 0.05, 0.06, 0.05], "a": [1, -1, 1, -1],
                         "eloszlas": ["normális"] * 4, "eltolas": [0, 0, 0, 0]})
    LSL, USL, SZINT = 0.40, 0.80, 3
lanc["eltolas"] = pd.to_numeric(lanc["eltolas"], errors="coerce").fillna(0)
lanc["sigma"] = np.where(lanc["eloszlas"] == "egyenletes", lanc["tur"] / np.sqrt(3), lanc["tur"] / SZINT)
Z0 = (lanc.a * lanc.nevleges).sum()
WC = (lanc.a.abs() * lanc.tur).sum()
sZ = np.sqrt(((lanc.a * lanc.sigma) ** 2).sum())
mZ = Z0 + (lanc.a * lanc.eltolas).sum()
print(f"Névleges: {Z0:.3f}; legrosszabb eset: {Z0 - WC:.3f}–{Z0 + WC:.3f} ({'teljesül' if Z0 - WC >= LSL and Z0 + WC <= USL else 'NEM teljesül'})")
print(f"RSS (3σ): ±{3 * sZ:.3f} → {mZ - 3 * sZ:.3f}–{mZ + 3 * sZ:.3f}; σ = {sZ:.4f}; Cp = {(USL - LSL) / (6 * sZ):.2f}; "
      f"Cpk = {min(USL - mZ, mZ - LSL) / (3 * sZ):.2f}; határon kívül (normális közelítés): {(norm.cdf((LSL - mZ) / sZ) + norm.sf((USL - mZ) / sZ)) * 1e6:.2f} ppm")
'''),
    md("## Monte Carlo-szimuláció"),
    code('''
rng = np.random.default_rng(3)
N = 1_000_000
def szimulal(lanc, eltolas_kulon=None):
    Z = np.zeros(N)
    for i, t in lanc.iterrows():
        kozep = t.nevleges + (t.eltolas if eltolas_kulon is None or eltolas_kulon[0] != i else eltolas_kulon[1])
        x = rng.uniform(kozep - t.tur, kozep + t.tur, N) if t.eloszlas == "egyenletes" else rng.normal(kozep, t.sigma, N)
        Z += t.a * x
    return Z
Z = szimulal(lanc)
ki = np.mean((Z < LSL) | (Z > USL))
print(f"Monte Carlo: átlag {Z.mean():.4f}, szórás {Z.std():.4f}, határon kívül {ki * 1e6:.1f} ppm")
hozz = (lanc.a * lanc.sigma) ** 2 / sZ ** 2
print("Szóráshozzájárulás:", {t: f"{h:.0%}" for t, h in zip(lanc.tag, hozz)})

eltolasok = np.linspace(0, lanc.tur.iloc[0], 9)
kiesés = []
for d in eltolasok:
    m = mZ + lanc.a.iloc[0] * d
    kiesés.append((norm.cdf((LSL - m) / sZ) + norm.sf((USL - m) / sZ)) * 1e6)
hatar = next((d for d, k in zip(eltolasok, kiesés) if k > 63), None)   # 63 ppm: a ±4σ-s folyamat kiesése
print("Az első tag középérték-eltolódásának hatása [ppm]:", {round(float(d), 3): round(float(k), 1) for d, k in zip(eltolasok, kiesés)})
print("Az első eltolódás, amelynél a kiesés 63 ppm fölé nő:", f"{hatar:.3f}" if hatar is not None else "a vizsgált tartományban nem éri el")

# változat: a síklapúság egyenletes eloszlással
v = lanc.copy(); v.loc[v.index[-1], "eloszlas"] = "egyenletes"
Zv = szimulal(v)
print(f"Ha az utolsó tag egyenletes eloszlású: szórás {Zv.std():.4f}, határon kívül {np.mean((Zv < LSL) | (Zv > USL)) * 1e6:.1f} ppm")
'''),
    md("## Ábra"),
    code('''
fig, axs = plt.subplots(1, 3, figsize=(15, 4.3), gridspec_kw={"width_ratios": [1.4, 1, 1]})
ax = axs[0]
ax.hist(Z[:200_000], bins=120, density=True, color="#A9C4DE")
for x, c in ((LSL, "#B83A3A"), (USL, "#B83A3A")):
    ax.axvline(x, color=c, ls="--")
ax.hlines(0.5, Z0 - WC, Z0 + WC, color="#E07B39", lw=3, label="legrosszabb eset")
ax.hlines(1.2, mZ - 3 * sZ, mZ + 3 * sZ, color="#3E8E63", lw=3, label="RSS (±3σ)")
ax.set_xlabel("eredő méret"); ax.set_ylabel("sűrűség"); ax.legend(fontsize=8)
ax.set_title("Monte Carlo-eloszlás a követelmény határaival", fontsize=10)
ax = axs[1]
s = np.argsort(hozz.to_numpy())
ax.barh(lanc.tag.to_numpy()[s], hozz.to_numpy()[s] * 100, color="#285780")
ax.set_xlabel("hozzájárulás az eredő szórásnégyzethez [%]"); ax.set_title("Melyik tag számít?", fontsize=10)
ax = axs[2]
ax.semilogy(eltolasok, np.maximum(kiesés, 1e-3), "o-", color="#B83A3A")
ax.axhline(63, color="#999999", ls=":"); ax.text(eltolasok[0], 75, "63 ppm (±4σ-s folyamat)", fontsize=8)
ax.set_xlabel(f"{lanc.tag.iloc[0]}: középérték-eltolódás"); ax.set_ylabel("határon kívül [ppm]")
ax.set_title("Érzékenység a középérték eltolódására", fontsize=10); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("turesek.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A legrosszabb eset (0,36–0,84 mm) nem teljesíti a 0,40–0,80 mm-es követelményt, a statisztikus számítás (0,48–0,72 mm, $C_p = 1{,}63$) igen; a Monte Carlo-szimuláció ezt megerősíti.
- Az eredő szórás legnagyobb része a tömítés vastagságából jön: a beszállító folyamatszabályozása itt a leghatékonyabb.
- A tömítés vastagságának középérték-eltolódása gyorsan növeli a kiesést: 0,04 mm-nél még mintegy 44 ppm, 0,05 mm-nél már 119 ppm, a teljes tűrésnyi (0,08 mm) eltolódásnál 1600 ppm fölött. Ezért kötötte ki a csapat a beszállítónál a statisztikai folyamatszabályozást. Ha a síklapúsági eltérés egyenletes eloszlású, az eredő szórás nő: az eloszlás megválasztása is számít.
"""),
]
