from _kozos import BETOLTO, code, fejresz, md

NEV = "tpm_kovetes"
CIM = "Műszaki teljesítménymérőszám (TPM) követése"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook egy műszaki teljesítménymérőszám (TPM) tervezett lefutását tűrésmezővel, a becsült vagy mért értékeket,
a küszöböt (követelményt) és a célértéket ábrázolja, kiszámítja a tervtől való eltérést és a küszöbig maradt
tartalékot, és lineáris trenddel előrejelzi a következő mérföldkövek várható értékét.

A beépített példa a KoboCella ciklusidejének követése (kézikönyv 6.4. szakasz).
""", sablon="moe_mop_tpm_sablon.xlsx", eszkozlap="Gyakorlati útmutató, MOE, MOP, TPM eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött moe_mop_tpm_sablon.xlsx „TPM-követés” lapja
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("moe_mop_tpm_sablon.xlsx")
    fej = pd.read_excel(fajl, sheet_name="TPM-követés", header=None, nrows=3)
    KUSZOB, CEL, IRANY, NEV_TPM = fej.iloc[2, 4], fej.iloc[2, 6], fej.iloc[2, 8], fej.iloc[2, 1]
    t = pd.read_excel(fajl, sheet_name="TPM-követés", header=4).iloc[:, :5].dropna(subset=["Mérföldkő"])
    t.columns = ["merfoldko", "terv", "also", "felso", "mert"]
else:
    KUSZOB, CEL, IRANY, NEV_TPM = 75.0, 70.0, "min", "ciklusidő [s]"
    t = pd.DataFrame({
        "merfoldko": ["SRR", "PDR", "CDR", "FAT", "SAT", "TRR", "ORR"],
        "terv": [83.0, 79.5, 76.8, 74.5, 73.8, 73.2, 73.2],
        "also": [80.0, 77.0, 74.5, 72.5, 72.0, 71.5, 71.5],
        "felso": [86.0, 82.0, 79.0, 76.5, 75.5, 75.0, 75.0],
        "mert": [84.0, 81.5, 78.2, 77.4, np.nan, np.nan, np.nan],
    })
t["eltérés"] = t["mert"] - t["terv"]
t["tűrésen belül"] = (t["mert"] >= t["also"]) & (t["mert"] <= t["felso"])
t["tartalék a küszöbig"] = (KUSZOB - t["mert"]) if IRANY == "min" else (t["mert"] - KUSZOB)
t
'''),
    md("## Trend-előrejelzés és ábra"),
    code('''
x = np.arange(len(t))
ismert = t["mert"].notna()
utolso = np.flatnonzero(ismert)[-3:]                     # az utolsó három mérés
m, b = np.polyfit(x[utolso], t.loc[utolso, "mert"], 1)
elore = m * x + b
elso_hianyzo = np.flatnonzero(~ismert)[0] if (~ismert).any() else len(t)

fig, ax = plt.subplots(figsize=(9, 4.8))
ax.fill_between(x, t["also"], t["felso"], color="#DDEFE4", label="tűrésmező")
ax.plot(x, t["terv"], "--", color="#3E8E63", label="tervezett lefutás")
ax.axhline(KUSZOB, color="#B83A3A", lw=1.6, label=f"küszöb: {KUSZOB}")
ax.axhline(CEL, color="#285780", lw=1.2, ls=":", label=f"célérték: {CEL}")
ax.plot(x[ismert], t.loc[ismert, "mert"], "o-", color="#E07B39", lw=2.2, label="becsült / mért")
ax.plot(x[utolso[0]:], elore[utolso[0]:], ":", color="#E07B39", label="trend (utolsó 3 pont)")
for i in np.flatnonzero(ismert & ~t["tűrésen belül"]):
    ax.annotate("tűrésen kívül", (x[i], t.loc[i, "mert"]), xytext=(8, 8), textcoords="offset points", color="#B83A3A")
ax.set_xticks(x, t["merfoldko"]); ax.set_ylabel(NEV_TPM); ax.grid(alpha=0.3)
ax.legend(fontsize=8, loc="upper right"); ax.set_title("TPM-követés")
plt.tight_layout(); plt.savefig("tpm_kovetes.png", bbox_inches="tight"); plt.show()

if elso_hianyzo < len(t):
    print(f"Trend szerint várható érték a(z) {t.loc[elso_hianyzo, 'merfoldko']} mérföldkőnél: {elore[elso_hianyzo]:.1f}")
    print(f"Az utolsó érték változása mérföldkövenként: {m:+.2f}")
'''),
    md("""
## Értelmezés

- Ha egy érték **kilép a tűrésmezőből**, beavatkozás kell, akkor is, ha a végső küszöb elvileg még teljesíthető. A tűrésmező a terv érettségéhez igazított elvárás.
- A trend-előrejelzés csak tájékoztató: a TPM-ek jellemzően lépcsőzetesen javulnak egy-egy tervezési beavatkozás után, nem lineárisan.
- A KoboCella esetében a FAT-on mért 77,4 s a tűrésmezőn kívül esett. A kobot pályájának átírása után a SAT-on 74,1 s lett (kézikönyv 6.4. szakasz). Írd be ezt az értéket, és futtasd újra a cellákat!
"""),
]
