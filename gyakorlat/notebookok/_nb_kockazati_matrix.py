from _kozos import BETOLTO, code, fejresz, md

NEV = "kockazati_matrix"
CIM = "Kockázati mátrix: a kockázatok elhelyezése, a mátrix felbontása és a kockázatok követése"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. a kockázati nyilvántartásból mátrixra rajzolja a kockázatokat a kezelés előtt és után;
2. ellenőrzi a zónák folytonosságát (egy lépés legfeljebb egy zónahatárt lépjen át), és Cox gondolatmenetét követve szimulációval megbecsüli, milyen gyakran rendezi helyesen a mátrix két véletlen kockázatot;
3. ábrázolja az összes kockázati pontszám havi alakulását a tervezett csökkenéshez képest.

A beépített példa a ForgácsTech MES-bevezetésének nyolc projektkockázata (kézikönyv 14. fejezet).
""", sablon="kockazati_matrix_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Kockázati mátrix eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött kockazati_matrix_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("kockazati_matrix_sablon.xlsx")
    sk = pd.read_excel(fajl, sheet_name="Skálák", header=None)
    PIROS, NARANCS = int(sk.iloc[11, 3]), int(sk.iloc[12, 3])
    ny = pd.read_excel(fajl, sheet_name="Nyilvántartás", header=3).iloc[:, :16]
    ny = ny[ny.iloc[:, 0].notna() & ny.iloc[:, 4].notna()]
    reg = pd.DataFrame({"id": ny.iloc[:, 0], "allitas": ny.iloc[:, 1], "S0": ny.iloc[:, 4], "P0": ny.iloc[:, 5],
                        "S1": ny.iloc[:, 10], "P1": ny.iloc[:, 11]})
    kv = pd.read_excel(fajl, sheet_name="Követés", header=3)
    honapok = [c for c in kv.columns[1:] if str(c).startswith("M")]
    kv = kv[kv.iloc[:, 0].astype(str).isin(set(reg["id"]) | {"Terv"})]
    kovetes = kv.set_index(kv.columns[0])[honapok].astype(float)
    terv = kovetes.loc["Terv"].to_numpy(); kovetes = kovetes.drop("Terv")
else:
    PIROS, NARANCS = 8, 6
    reg = pd.DataFrame({"id": ["K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8"],
                        "allitas": ["gépi interfészek hiánya", "az ütemező megkerülése", "beszállítói függés", "elavult normaidők",
                                    "WiFi-lefedettség", "a kulcsfelhasználó leterheltsége", "kibertámadás", "integrációs költségtúllépés"],
                        "S0": [3, 4, 4, 3, 2, 3, 4, 3], "P0": [4, 3, 2, 4, 3, 3, 2, 3],
                        "S1": [3, 3, 3, 2, 2, 3, 4, 3], "P1": [2, 2, 2, 2, 1, 2, 1, 2]})
    honapok = ["M0", "M1", "M2", "M3", "M4", "M5", "M6"]
    kovetes = pd.DataFrame({"K1": [12, 12, 9, 6, 6, 6, 6], "K2": [12, 12, 12, 12, 9, 6, 6], "K3": [8, 8, 6, 6, 6, 6, 6],
                            "K4": [12, 9, 9, 6, 4, 4, 4], "K5": [6, 6, 3, 2, 2, 2, 2], "K6": [9, 9, 9, 6, 6, 6, 6],
                            "K7": [8, 8, 8, 4, 4, 4, 4], "K8": [9, 9, 9, 9, 6, 6, 6]}, index=honapok).T
    terv = np.array([76, 70, 63, 57, 51, 44, 38])
for c in ("S0", "P0", "S1", "P1"):
    reg[c] = reg[c].astype(int)

def zona(s, p):
    return "elfogadhatatlan" if s + p >= PIROS else ("ALARP" if s + p >= NARANCS else "elfogadható")
SZIN = {"elfogadhatatlan": "#F6DEDE", "ALARP": "#FBE7D9", "elfogadható": "#DDEFE4"}
reg["zona0"] = [zona(s, p) for s, p in zip(reg.S0, reg.P0)]
reg["zona1"] = [zona(s, p) for s, p in zip(reg.S1, reg.P1)]
reg[["id", "allitas", "S0", "P0", "zona0", "S1", "P1", "zona1"]]
'''),
    md("## A mátrix folytonossága és felbontása"),
    code('''
# 1) folytonosság: szomszédos cellák zónaindexe legfeljebb 1-gyel tér el
ZI = {"elfogadható": 0, "ALARP": 1, "elfogadhatatlan": 2}
ugras = max(abs(ZI[zona(s, p)] - ZI[zona(s + ds, p + dp)])
            for s in range(1, 6) for p in range(1, 6) for ds, dp in ((1, 0), (0, 1)) if s + ds <= 5 and p + dp <= 5)
print("Folytonos zónák (egy lépés legfeljebb egy határ):", ugras <= 1)

# 2) felbontás Cox gondolatmenete szerint: a kategóriák mögött folytonos, nagyságrendi skálát feltételezünk
#    log10(gyakoriság) a P kategórián belül egyenletes, log10(súlyosság) az S kategórián belül egyenletes
rng = np.random.default_rng(1)
n = 200_000
lp = rng.uniform(-3, 2, (n, 2)); ls = rng.uniform(0, 5, (n, 2))
P = np.floor(lp + 3).astype(int) + 1; S = np.floor(ls).astype(int) + 1
z = np.vectorize(lambda s, p: ZI[zona(s, p)])(S, P)
valodi = lp + ls                                  # log10(kockázat)
kul_zona = z[:, 0] != z[:, 1]
helyes = kul_zona & (np.sign(z[:, 0] - z[:, 1]) == np.sign(valodi[:, 0] - valodi[:, 1]))
print(f"Két véletlen kockázat közül a mátrix {kul_zona.mean():.0%}-ban tesz különbséget (eltérő zóna);")
print(f"  ebből helyes sorrend: {helyes.sum() / kul_zona.sum():.1%}, hibás sorrend: {1 - helyes.sum() / kul_zona.sum():.1%}")
print(f"  {1 - kul_zona.mean():.0%}-ban azonos zónába sorolja őket, pedig a valódi kockázatuk átlagosan "
      f"{np.median(10 ** np.abs(valodi[~kul_zona, 0] - valodi[~kul_zona, 1])):.1f}-szeresen (medián) különbözik.")
'''),
    md("## Ábra"),
    code('''
fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1, 1.25]})
ax = axs[0]
for s in range(1, 6):
    for p in range(1, 6):
        ax.add_patch(Rectangle((p - 0.5, s - 0.5), 1, 1, facecolor=SZIN[zona(s, p)], edgecolor="white", lw=2))
eltol = {}
for _, r in reg.iterrows():
    k = (r.S0, r.P0); d = eltol.get(k, 0); eltol[k] = d + 1
    dx, dy = -0.3 + 0.2 * (d % 4), 0.25 - 0.25 * (d // 4)
    k1 = (r.S1, r.P1, "u"); d1 = eltol.get(k1, 0); eltol[k1] = d1 + 1
    dx1, dy1 = -0.3 + 0.2 * (d1 % 4), -0.25 + 0.25 * (d1 // 4)
    ax.annotate("", xy=(r.P1 + dx1, r.S1 + dy1), xytext=(r.P0 + dx, r.S0 + dy),
                arrowprops=dict(arrowstyle="->", color="#7FA6CC", lw=1))
    ax.plot(r.P0 + dx, r.S0 + dy, "o", color="#B83A3A", ms=5)
    ax.text(r.P0 + dx, r.S0 + dy + 0.12, r.id, fontsize=7, ha="center")
    ax.plot(r.P1 + dx1, r.S1 + dy1, "s", color="#3E8E63", ms=5)
ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.set_aspect("equal")
ax.set_xticks(range(1, 6)); ax.set_yticks(range(1, 6))
ax.set_xlabel("valószínűség (P)"); ax.set_ylabel("súlyosság (S)")
ax.set_title("Kockázatok a kezelés előtt (kör) és után (négyzet)", fontsize=10)

ax = axs[1]
x = np.arange(len(honapok))
for i, (rid, sor) in enumerate(kovetes.iterrows()):
    ax.plot(x, sor.to_numpy(), color="#B8CEE4", lw=1, label="kockázatonként" if i == 0 else None)
ax2 = ax.twinx()
ax2.plot(x, kovetes.sum().to_numpy(), "o-", color="#285780", lw=2.5, label="összesen (tény)")
ax2.plot(x, terv, "--", color="#E07B39", lw=2, label="összesen (terv)")
ax.set_xticks(x); ax.set_xticklabels(honapok); ax.set_ylabel("kockázatonkénti pontszám (S × P)")
ax2.set_ylabel("összes pontszám"); ax2.legend(fontsize=8, loc="upper right"); ax.legend(fontsize=8, loc="lower left")
ax.set_title("A kockázati pontszámok havi alakulása", fontsize=10); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("kockazati_matrix.png", bbox_inches="tight", dpi=150); plt.show()

lassu = [rid for rid, sor in kovetes.iterrows() if sor.iloc[len(sor) // 2] >= sor.iloc[0]]
print("A félidőben még nem csökkent kockázatok:", lassu)
'''),
    md("""
## Értelmezés

- A ForgácsTech nyolc kockázatából hét a tűrhető (ALARP) tartományból indult; a tervezett intézkedések után mind az elfogadható zónába kerül. Az összes pontszám 76-ról 40-re csökkent, a tervvel nagyjából összhangban.
- A félidőben két kockázat (K2, K8) még nem csökkent. A K2 (az ütemező megkerülése) a kézikönyv esete szerint a próbaüzem első hónapjában is lassan csökkent; az ilyen kockázatnál kell a beavatkozási küszöbhöz kötött tartalékintézkedés.
- A szimuláció a mátrix felbontásának korlátját mutatja: a véletlen kockázatpárok mintegy harmadát azonos zónába sorolja, holott valódi kockázatuk mediánban hatszorosan eltér; az eltérő zónába soroltak kis részénél (itt kb. 1%) a sorrend is hibás. Az eredmény a feltevésen múlik, hogy mindkét skála nagyságrendi lépésekből áll; ha a súlyossági kategóriák nem ilyenek, a hibás sorrendek aránya nő. Ez Cox (2008) megállapításának egyszerű illusztrációja: a mátrix előszűrésre és kommunikációra jó, a változatok közötti finom döntésre nem.
"""),
]
