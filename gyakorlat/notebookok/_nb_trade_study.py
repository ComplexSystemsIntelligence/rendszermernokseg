from _kozos import BETOLTO, code, fejresz, md

NEV = "trade_study"
CIM = "Súlyozott értékelés (trade study): pontszámok, érzékenység, Monte Carlo"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook egy súlyozott értékelés adataiból

1. lineáris hasznossági függvényekkel 0–10 pontszámot számol, majd súlyozott összpontszámot és rangsort;
2. **egytényezős érzékenységvizsgálatot** végez minden kritériumra: megkeresi azt a súlyt, amelynél a rangsor élén változás történik;
3. **Monte Carlo-szimulációval** a súlyokat az alapsúlyok körül szóródó Dirichlet-eloszlásból újramintavételezi, és megszámolja, hányszor nyer az egyes alternatíva.

A beépített példa a KoboCella három koncepciója (kézikönyv 10. fejezet).
""", sablon="trade_study_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Súlyozott értékelés eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött trade_study_sablon.xlsx
N_SZIM = 5000          # Monte Carlo-ismétlések
KONCENTRACIO = 50      # nagyobb érték = a súlyok kevésbé szórnak az alapsúlyok körül
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("trade_study_sablon.xlsx")
    kr = pd.read_excel(fajl, sheet_name="Kritériumok", header=3).dropna(subset=["Kód"])
    kr.columns = ["kod", "nev", "egyseg", "suly", "tipus", "rossz", "jo"]
    ev = pd.read_excel(fajl, sheet_name="Értékelés", header=None)
    alternativak = [a for a in ev.iloc[3, 2:8] if isinstance(a, str)]
    ertek = ev.iloc[4:4 + len(kr), 2:2 + len(alternativak)].to_numpy()
    sk = pd.read_excel(fajl, sheet_name="Skála", header=3).dropna(subset=["Szint"])
    skala = dict(zip(sk["Szint"], sk["Pontszám (0–10)"]))
else:
    kr = pd.DataFrame({
        "kod": ["K1", "K2", "K3", "K4", "K5", "K6"],
        "nev": ["ciklusidő", "utómunka-arány", "törzshajlítás", "beruházás", "átállási idő", "technikai kockázat"],
        "suly": [20, 20, 15, 15, 15, 15],
        "tipus": ["lineáris"] * 5 + ["szóbeli"],
        "rossz": [90, 3.5, 45, 120, 30, np.nan], "jo": [45, 0.5, 10, 0, 0, np.nan]})
    alternativak = ["A: együttműködő cella", "B: fix állomás", "D: zárt robotcella"]
    ertek = np.array([[58.6, 52, 48], [0.8, 0.7, 0.6], [15, 15, 10], [78, 95, 110], [5, 30, 20],
                      ["közepes", "alacsony", "magas"]], dtype=object)
    skala = {"alacsony": 9, "közepes": 6, "magas": 2}

def pont(sor, x):
    if sor["tipus"] == "szóbeli":
        return float(skala[x])
    return round(float(np.clip(10 * (float(x) - sor["rossz"]) / (sor["jo"] - sor["rossz"]), 0, 10)), 1)

U = np.array([[pont(kr.iloc[i], ertek[i, j]) for j in range(len(alternativak))] for i in range(len(kr))]) + 0.0
W = kr["suly"].to_numpy(float)
osszpont = W @ U / W.sum() + 1e-9   # a kerekítési határesetek miatt
tabla = pd.DataFrame(U, index=kr["kod"] + " " + kr["nev"], columns=alternativak)
tabla.loc["súlyozott összpontszám"] = np.round(osszpont, 2)
tabla
'''),
    md("## Egytényezős érzékenységvizsgálat"),
    code('''
def pontszam_suly(k, w):
    Wn = W * (W.sum() - w) / (W.sum() - W[k]); Wn[k] = w
    return Wn @ U / Wn.sum()

alap_nyertes = int(np.argmax(osszpont))
sorok = []
for k in range(len(W)):
    racs = np.round(np.arange(0, 60.01, 0.1), 1)
    nyertes = [int(np.argmax(pontszam_suly(k, w))) for w in racs]
    lefele = [w for w, n in zip(racs, nyertes) if w <= W[k] and n != alap_nyertes]
    felfele = [w for w, n in zip(racs, nyertes) if w >= W[k] and n != alap_nyertes]
    sorok.append({"kritérium": kr["kod"][k], "alapsúly": W[k],
                  "váltás lefelé (súly alatt)": (max(lefele) + 0.1) if lefele else "nincs",
                  "váltás felfelé (súly fölött)": min(felfele) if felfele else "nincs (60-ig)",
                  "új nyertes": alternativak[nyertes[racs.tolist().index(min(felfele))]] if felfele else
                                (alternativak[nyertes[racs.tolist().index(max(lefele))]] if lefele else "–")})
pd.DataFrame(sorok)
'''),
    md("## Monte Carlo-szimuláció a súlyokra"),
    code('''
rng = np.random.default_rng(42)
alap = W / W.sum()
nyer = np.zeros(len(alternativak), int)
for _ in range(N_SZIM):
    w = rng.dirichlet(alap * KONCENTRACIO)
    nyer[np.argmax(w @ U)] += 1
arany = nyer / N_SZIM
for a, p in zip(alternativak, arany):
    print(f"{a}: {p:.1%}")

fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
axs[0].barh(alternativak, osszpont, color="#4F7FAD"); axs[0].invert_yaxis()
for i, v in enumerate(osszpont):
    axs[0].text(v + 0.05, i, f"{v:.2f}", va="center", fontsize=9)
axs[0].set_xlim(0, 10); axs[0].set_title("Súlyozott összpontszám (alapsúlyok)", fontsize=10)
axs[1].barh(alternativak, 100 * arany, color="#E07B39"); axs[1].invert_yaxis()
for i, v in enumerate(arany):
    axs[1].text(100 * v + 1, i, f"{v:.0%}", va="center", fontsize=9)
axs[1].set_xlim(0, 105); axs[1].set_title(f"Első hely gyakorisága ({N_SZIM} súlyminta)", fontsize=10)
axs[1].set_xlabel("%")
plt.tight_layout(); plt.savefig("trade_montecarlo.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A KoboCella példájában az együttműködő cella (A) 7,16 ponttal nyer a fix állomás (B, 6,50) és a zárt robotcella (D, 6,22) előtt.
- Az egytényezős vizsgálat szerint a rangsor leginkább az átállási idő (K5) súlyára érzékeny: 7,6 alatt a B kerül az élre. Ezért kellett a változatváltások várható gyakoriságát a gyártásvezetővel tisztázni.
- A Monte Carlo-szimulációban az A az esetek mintegy 92%-ában első. Ez nem „valószínűség, hogy az A a jó döntés”, hanem annak mértéke, mennyire robusztus a rangsor a súlyok bizonytalanságával szemben.
- Próbáld ki: csökkentsd a `KONCENTRACIO` értékét 10-re (nagyobb bizonytalanság a súlyokban), és figyeld az arányok változását!
"""),
]
