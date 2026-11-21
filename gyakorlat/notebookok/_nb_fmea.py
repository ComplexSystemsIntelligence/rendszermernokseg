from _kozos import BETOLTO, code, fejresz, md

NEV = "fmea"
CIM = "FMEA: rangsorolás RPN-nel és súlyossággal, az intézkedések hatása, az RPN-skála korlátai"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. az FMEA-munkalapból kiszámítja az RPN-t és a prioritást (egyszerűsített szabály: 9–10-es súlyosságnál, ha az előfordulás legalább 2, mindig magas), az intézkedés előtt és után;
2. Pareto-ábrán mutatja a hibamódok RPN-jét és az intézkedések hatását;
3. megkeresi az azonos RPN-ű, de eltérő súlyosságú hibamódokat;
4. a teljes 10 × 10 × 10-es térben megmutatja, miért problémás az RPN-skála (Bowles, 2003): hány különböző érték fordul elő, és ezek hogyan oszlanak el.

A beépített példa a KoboCella folyamat- és cella-FMEA-jának részlete (kézikönyv 15. fejezet).
""", sablon="fmea_sablon.xlsx", eszkozlap="Gyakorlati útmutató, FMEA eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött fmea_sablon.xlsx
''' + BETOLTO + '''
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("fmea_sablon.xlsx")
    ut = pd.read_excel(fajl, sheet_name="Útmutató", header=None)
    MAGAS, KOZEPES = float(ut.iloc[19, 1]), float(ut.iloc[20, 1])
    f = pd.read_excel(fajl, sheet_name="FMEA", header=3).iloc[:, :22]
    f.columns = ["az", "elem", "funkcio", "hibamod", "hatas", "S", "ok", "megelozo", "O", "eszlelo", "D", "RPN", "prio",
                 "javaslat", "felelos", "hatarido", "vegrehajtott", "S2", "O2", "D2", "RPN2", "prio2"]
    f = f[f["hibamod"].notna() & f["S"].notna()]
else:
    MAGAS, KOZEPES = 100, 40
    f = pd.DataFrame({
        "az": ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"],
        "hibamod": ["fordított fedél", "hibás darab a kiadóba", "rossz típusprogram", "hiányzó csavar", "alacsony nyomaték",
                    "a motorház nem ül fel", "a szkenner nem érzékel", "ferde fedél", "hiányzó nyomatékadat"],
        "S": [8, 8, 7, 8, 8, 4, 10, 5, 6], "O": [5, 3, 3, 5, 4, 6, 2, 3, 3], "D": [7, 8, 5, 2, 2, 2, 6, 2, 4],
        "S2": [8, 8, 7, 8, 8, None, 10, None, 6], "O2": [1, 3, 1, 3, 2, None, 1, None, 1], "D2": [1, 2, 5, 2, 2, None, 2, None, 4]})
for c in ("S", "O", "D", "S2", "O2", "D2"):
    f[c] = pd.to_numeric(f[c], errors="coerce")
# intézkedés nélküli sorok: a régi érték marad
for a, b in (("S", "S2"), ("O", "O2"), ("D", "D2")):
    f[b] = f[b].fillna(f[a])

def prio(s, o, d):
    rpn = s * o * d
    if s >= 9 and o >= 2:
        return "magas (súlyosság)"
    return "magas" if rpn > MAGAS else ("közepes" if rpn >= KOZEPES else "alacsony")
f["RPN"] = f.S * f.O * f.D; f["RPN2"] = f.S2 * f.O2 * f.D2
f["prio"] = [prio(*x) for x in zip(f.S, f.O, f.D)]; f["prio2"] = [prio(*x) for x in zip(f.S2, f.O2, f.D2)]
f[["az", "hibamod", "S", "O", "D", "RPN", "prio", "S2", "O2", "D2", "RPN2", "prio2"]]
'''),
    md("## Azonos RPN, eltérő kockázat"),
    code('''
for nev, oszl, sz in (("előtt", "RPN", "S"), ("után", "RPN2", "S2")):
    for rpn, g in f.groupby(oszl):
        if len(g) > 1 and g[sz].nunique() > 1:
            print(f"{nev}: RPN = {rpn:.0f}: " + "; ".join(f"{r.az} {r.hibamod} (S={r[sz]:.0f})" for _, r in g.iterrows()))
'''),
    md("## Az RPN-skála tulajdonságai"),
    code('''
osszes = np.array([a * b * c for a, b, c in itertools.product(range(1, 11), repeat=3)])
ertekek, db = np.unique(osszes, return_counts=True)
print(f"Különböző RPN-értékek száma: {len(ertekek)} (az 1–1000 tartományban)")
print(f"A kombinációk mediánja: {np.median(osszes):.0f}; 100 fölött: {np.mean(osszes > 100):.0%}; 40 alatt: {np.mean(osszes < 40):.0%}")
print(f"A különböző értékek közül {np.sum(ertekek <= 333)} a skála alsó harmadába esik, {np.sum(ertekek > 500)} 500 fölé.")
print("Leggyakoribb értékek:", {int(e): int(n) for e, n in zip(ertekek[np.argsort(-db)][:5], np.sort(db)[::-1][:5])})
'''),
    md("## Ábra"),
    code('''
SZIN = {"magas (súlyosság)": "#7A5C99", "magas": "#B83A3A", "közepes": "#E07B39", "alacsony": "#3E8E63"}
fig, axs = plt.subplots(1, 3, figsize=(15, 4.6), gridspec_kw={"width_ratios": [1.3, 1, 1.2]})
d = f.sort_values("RPN", ascending=False)
x = np.arange(len(d))
axs[0].bar(x - 0.2, d.RPN, 0.4, color=[SZIN[p] for p in d.prio])
axs[0].bar(x + 0.2, d.RPN2, 0.4, color=[SZIN[p] for p in d.prio2], alpha=0.55, hatch="//", edgecolor="white")
axs[0].axhline(MAGAS, color="#B83A3A", ls="--", lw=1); axs[0].axhline(KOZEPES, color="#E07B39", ls=":", lw=1)
axs[0].set_xticks(x); axs[0].set_xticklabels(d.az, fontsize=8); axs[0].set_ylabel("RPN")
from matplotlib.patches import Patch
kezelok = [Patch(facecolor=c, label=p) for p, c in SZIN.items()] + [Patch(facecolor="#BBBBBB", hatch="//", edgecolor="white", label="intézkedés után")]
axs[0].legend(handles=kezelok, fontsize=7, ncol=2); axs[0].set_title("RPN az intézkedések előtt és után", fontsize=10)

ax = axs[1]
foglalt = {}
for _, r in f.iterrows():
    if (r.S, r.O) != (r.S2, r.O2):
        ax.annotate("", xy=(r.O2, r.S2), xytext=(r.O, r.S), arrowprops=dict(arrowstyle="->", color="#7FA6CC"))
    ax.scatter(r.O, r.S, s=25 * r.D, color=SZIN[r.prio], alpha=0.8, edgecolor="black", lw=0.4)
    k = foglalt.get((r.O, r.S), 0); foglalt[(r.O, r.S)] = k + 1
    ax.text(r.O + 0.15, r.S + 0.15 - 0.45 * k, r.az, fontsize=7)
ax.axhspan(8.5, 10.5, color="#ECE5F3", zorder=0)
ax.set_xlim(0.5, 10.5); ax.set_ylim(0.5, 10.5); ax.set_xlabel("előfordulás (O)"); ax.set_ylabel("súlyosság (S)")
ax.set_title("Súlyosság–előfordulás (pontméret: D)", fontsize=10); ax.grid(alpha=0.3)

ax = axs[2]
ax.bar(ertekek, db, width=4, color="#285780")
ax.set_xlabel("RPN"); ax.set_ylabel("kombinációk száma (1000-ből)")
ax.set_title(f"Az RPN-skála: csak {len(ertekek)} különböző érték", fontsize=10)
plt.tight_layout(); plt.savefig("fmea_elemzes.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A kezdeti értékelésben négy hibamód kapott magas prioritást; a legmagasabb RPN-t a fordított fedél kapta (280), amelyet a hibabiztos kialakítás lényegében megszüntetett. A szkenner hibamódja (F7) RPN szerint csak a magas határ fölött volt, de a 10-es súlyosság miatt az egyszerűsített szabály akkor is magas prioritást adna, ha az RPN alacsonyabb lenne.
- Az intézkedések után a hiányzó csavar (F4) és a motorház behelyezése (F6) RPN-je azonos (48), pedig az előbbi a vevőnél tömítetlen motort, az utóbbi csak időveszteséget okoz. Ez Bowles kritikájának gyakorlati példája: az RPN önmagában nem elég, a súlyosságot külön kell figyelni.
- Az 1000 lehetséges kombináció csak 120 különböző RPN-t ad. A különböző értékek a skála alsó részén sűrűsödnek (85 a 333 alatti tartományban, csak 17 van 500 fölött), a skála felső része lyukas. A kombinációk mediánja 105, vagyis a 100-as küszöb a lehetséges esetek felét magasnak minősíti. A küszöbök tehát nem egyenletes kockázati lépéseket jelölnek.
"""),
]
