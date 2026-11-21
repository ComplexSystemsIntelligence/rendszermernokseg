from _kozos import BETOLTO, code, fejresz, md

NEV = "koltseg_haszon"
CIM = "Költség–haszon elemzés: jelenérték, növekményes elemzés, Monte Carlo"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. kiszámítja az alternatívák költségeinek és (kockázattal korrigált) hasznainak jelenértékét, a B/C arányt és a nettó jelenértéket;
2. elvégzi a **növekményes elemzést** a mérnöki gazdaságtan eljárása szerint (védő–kihívó összevetés; Sullivan és mtsai, 2019);
3. **Monte Carlo-szimulációval** vizsgálja, mennyire biztos az eredmény, ha a beruházás és az éves haszon becslése bizonytalan (háromszögeloszlás: pesszimista, legvalószínűbb, optimista érték).

A beépített példa a ForgácsTech három MES-koncepciója (kézikönyv 10. fejezet).
""", sablon="koltseg_haszon_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Költség–haszon elemzés eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött koltseg_haszon_sablon.xlsx
N_SZIM = 10000
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("koltseg_haszon_sablon.xlsx")
    p = pd.read_excel(fajl, sheet_name="Alternatívák", header=None)
    r, T = float(p.iloc[2, 1]), int(p.iloc[3, 1])
    a = p.iloc[6:14, :6].dropna(subset=[0])
    df = pd.DataFrame({"kód": a[0], "név": a[1], "beruházás": a[2].astype(float), "működtetés": a[3].astype(float),
                       "haszon": a[4].astype(float), "f": a[5].astype(float)})
else:
    r, T = 0.08, 5
    df = pd.DataFrame({"kód": ["M1", "M2", "M3"], "név": ["teljes MES", "gépgyártói + MES", "fokozatos"],
                       "beruházás": [42, 30, 14], "működtetés": [4, 6, 3], "haszon": [28, 22, 15], "f": [0.75, 0.5, 1.0]})
# a Monte Carlo bizonytalansági sávjai: (pesszimista, legvalószínűbb, optimista) – szorzóként a pontbecsléshez;
# a haszonsávok várható értéke megegyezik a kockázati szorzóval (0,75; 0,5; 1,0), így a két elemzés összevethető
SAV_BERUHAZAS = {"M1": (0.95, 1.0, 1.25), "M2": (0.95, 1.0, 1.35), "M3": (0.95, 1.0, 1.2)}
SAV_HASZON = {"M1": (0.35, 0.85, 1.05), "M2": (0.2, 0.5, 0.8), "M3": (0.8, 1.05, 1.15)}   # várható értékük = az f szorzó
'''),
    md("## Jelenérték, B/C, nettó jelenérték"),
    code('''
af = sum(1 / (1 + r) ** t for t in range(1, T + 1))
df["C"] = df["beruházás"] + df["működtetés"] * af
df["B"] = df["haszon"] * df["f"] * af
df["B/C"] = df["B"] / df["C"]
df["NPV"] = df["B"] - df["C"]
print(f"Annuitástényező ({T} év, {r:.0%}): {af:.4f}")
df.round(2)
'''),
    md("## Növekményes elemzés (védő–kihívó)"),
    code('''
jelolt = df[df["B/C"] >= 1].sort_values("C").reset_index(drop=True)
vedo = jelolt.iloc[0]
lepesek = []
for _, kihivo in jelolt.iloc[1:].iterrows():
    dB, dC = kihivo["B"] - vedo["B"], kihivo["C"] - vedo["C"]
    megeri = dB / dC > 1
    lepesek.append({"védő": vedo["kód"], "kihívó": kihivo["kód"], "ΔB": round(dB, 1), "ΔC": round(dC, 1),
                    "ΔB/ΔC": round(dB / dC, 2), "megéri?": "igen" if megeri else "nem"})
    if megeri:
        vedo = kihivo
print("Kiesett (B/C < 1):", list(df.loc[df["B/C"] < 1, "kód"]))
print("Preferált alternatíva:", vedo["kód"], "-", vedo["név"])
pd.DataFrame(lepesek)
'''),
    md("## Monte Carlo: mennyire biztos az eredmény?"),
    code('''
rng = np.random.default_rng(7)
npv = {}
for _, a in df.iterrows():
    sb, sh = SAV_BERUHAZAS.get(a["kód"], (1, 1, 1)), SAV_HASZON.get(a["kód"], (1, 1, 1))
    beruh = a["beruházás"] * rng.triangular(*sb, N_SZIM)
    hasz = a["haszon"] * rng.triangular(*sh, N_SZIM)            # a kockázatot itt az eloszlás hordozza, nem az f szorzó
    npv[a["kód"]] = hasz * af - (beruh + a["működtetés"] * af)
npv = pd.DataFrame(npv)
legjobb = npv.idxmax(axis=1).value_counts(normalize=True)
osszegzes = pd.DataFrame({"NPV medián": npv.median(), "NPV 10. percentilis": npv.quantile(0.1),
                          "P(NPV > 0)": (npv > 0).mean(), "P(legnagyobb NPV)": legjobb}).fillna(0)
print(osszegzes.round(2))

fig, ax = plt.subplots(figsize=(8.5, 4.2))
szin = {"M1": "#285780", "M2": "#999999", "M3": "#E07B39"}
for k in npv.columns:
    ax.hist(npv[k], bins=60, alpha=0.55, color=szin.get(k, "#3E8E63"), label=f"{k}: medián {npv[k].median():.0f} MFt")
ax.axvline(0, color="#B83A3A", lw=1.2)
ax.set_xlabel("nettó jelenérték [MFt]"); ax.set_ylabel("gyakoriság"); ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax.set_title(f"A nettó jelenérték eloszlása ({N_SZIM} szimuláció)", fontsize=10)
plt.tight_layout(); plt.savefig("kh_montecarlo.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A pontbecslések szerint az M2 B/C aránya 1 alatt van, ezért kiesik. Az M3-ról az M1-re lépés növekménye 0,75: a 32 MFt többletköltség csak 24 MFt többlethasznot hoz, így az M3 a preferált.
- A Monte Carlo-szimulációban a kockázatot nem az f szorzó, hanem a haszon ferde eloszlása hordozza: az M1-nél a haszon pesszimista esete jóval a legvalószínűbb érték alatt van (bevezetési kockázat). A beépített példában az M3 nettó jelenértéke gyakorlatilag mindig pozitív, és az esetek mintegy kétharmadában ez a legnagyobb; az M1-nél a 10. percentilis már nulla körül van, vagyis tízből egy esetben a beruházás nem térül meg öt év alatt.
- A sávokat (`SAV_BERUHAZAS`, `SAV_HASZON`) a csapat szakértői becslései alapján kell megadni; a Delphi-módszer erre is alkalmas.
"""),
]
