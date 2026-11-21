from _kozos import BETOLTO, code, fejresz, md

NEV = "folyamatabra_vsm"
CIM = "Értékáram-térkép: idővonal, folyamathatékonyság, Little-ellenőrzés, jelenlegi és jövőbeli állapot"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. beolvassa a folyamat lépéseit a műveleti idővel, a lépések előtti várakozással és a várakozó egységek számával;
2. kiszámítja az átfutási időt, a folyamathatékonyságot és az értékteremtő arányt, és a Little-törvénnyel ellenőrzi a térképet;
3. megrajzolja a jelenlegi és a jövőbeli állapot egyszerűsített értékáram-térképét lépcsős idővonallal;
4. összeveti a két állapotot, és megmutatja, hol csökkent a várakozás.

A beépített példa a ForgácsTech egy rendelésének értékárama (kézikönyv 19. fejezet; Rother és Shook, 1999).
""", sablon="folyamatabra_vsm_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Folyamatábra és értékáram-térkép eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött folyamatabra_vsm_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
import textwrap
'''),
    md("## Adatok"),
    code('''
OSZL = ["lepes", "szimbolum", "eroforras", "muvelet_h", "beallitas_h", "varakozas_nap", "varo_egyseg", "ertek"]

def lap_olvas(fajl, lap):
    d = pd.read_excel(fajl, sheet_name=lap, header=6).iloc[:, :8]
    d.columns = OSZL
    d = d[d["lepes"].notna() & d["muvelet_h"].notna()].reset_index(drop=True)
    p = pd.read_excel(fajl, sheet_name=lap, header=None, nrows=5)
    return d, float(p.iloc[2, 1]), float(p.iloc[3, 1]), float(p.iloc[4, 1])

if SAJAT_SABLON:
    fajl = sablon_betoltese("folyamatabra_vsm_sablon.xlsx")
    jelen, ORA, I_j, R_j = lap_olvas(fajl, "Jelenlegi")
    jovo, _, I_f, R_f = lap_olvas(fajl, "Jövőbeli")
else:
    lepesek = ["gyártás-\\nelőkészítés", "anyag-\\nelőkészítés", "megmunkálás", "sorjázás,\\nmosás", "minőség-\\nellenőrzés", "csomagolás,\\nkiszállítás"]
    jelen = pd.DataFrame({"lepes": lepesek, "muvelet_h": [0.8, 0.3, 3.2, 0.5, 0.6, 0.4], "beallitas_h": [0, 0.05, 0.8, 0, 0, 0],
                          "varakozas_nap": [1.5, 2.5, 3.0, 1.0, 1.0, 1.0], "varo_egyseg": [9, 15, 18, 6, 6, 6],
                          "ertek": ["szükséges", "értékteremtő", "értékteremtő", "értékteremtő", "szükséges", "szükséges"]})
    jovo = jelen.copy()
    jovo["muvelet_h"] = [0.8, 0.3, 2.53, 0.5, 0.6, 0.4]
    jovo["beallitas_h"] = [0, 0.05, 0.13, 0, 0, 0]
    jovo["varakozas_nap"] = [0.5, 0.5, 1.5, 0.5, 0.5, 0.5]
    jovo["varo_egyseg"] = [3, 3, 9, 3, 3, 3]
    ORA, I_j, R_j, I_f, R_f = 15, 60, 6, 24, 6

def osszesit(d, I, R, nev):
    atf_nap = d.varakozas_nap.sum()
    atf_h = atf_nap * ORA
    m = d.muvelet_h.sum()
    va = d.loc[d.ertek == "értékteremtő", "muvelet_h"].sum()
    little = I / R if R else np.nan
    print(f"{nev}: műveleti idő {m:.2f} óra (értékteremtő {va:.2f}, beállítás {d.beallitas_h.sum():.2f}); "
          f"átfutás {atf_nap:.1f} nap = {atf_h:.0f} óra; folyamathatékonyság {m / atf_h:.1%}; értékteremtő arány {va / atf_h:.1%}")
    print(f"   Little-ellenőrzés: I/R = {I:.0f}/{R:.1f} = {little:.1f} nap (térkép: {atf_nap:.1f} nap); "
          f"leghosszabb várakozás: {d.varakozas_nap.max():.1f} nap, {d.lepes[d.varakozas_nap.idxmax()].replace(chr(10), ' ')}")
    # a lépésenkénti várakozás és a várakozó egységek összhangja: egységek ≈ várakozás × R
    elter = (d.varo_egyseg - d.varakozas_nap * R).abs().max()
    if elter > 0.5:
        print(f"   Figyelem: a várakozó egységek és a várakozási idő legfeljebb {elter:.1f} egységgel tér el a Little-törvénytől.")
    return dict(muvelet=m, va=va, atf_nap=atf_nap, atf_h=atf_h, pce=m / atf_h, little=little)

S_j = osszesit(jelen, I_j, R_j, "Jelenlegi")
S_f = osszesit(jovo, I_f, R_f, "Jövőbeli ")
'''),
    md("## Értékáram-térkép és összevetés"),
    code('''
def rajz_vsm(ax, d, S, cim, kiemelt=None):
    n = len(d)
    lx = 2.6
    for i, t in d.iterrows():
        x = i * lx + 1.3
        szin = "#FBE3D2" if (kiemelt is not None and i == kiemelt) else "#E6EEF6"
        ax.add_patch(FancyBboxPatch((x - 1.0, 2.6), 2.0, 1.0, boxstyle="round,pad=0.02", fc=szin, ec="#285780", lw=1))
        ax.text(x, 3.1, textwrap.fill(t.lepes.replace(chr(10), " ").replace("- ", "-"), 15), ha="center", va="center", fontsize=7.5)
        xt = x - 1.3
        ax.add_patch(Polygon([[xt - 0.25, 3.75], [xt + 0.25, 3.75], [xt, 4.2]], closed=True, fc="#FBE3D2", ec="#E07B39"))
        ax.text(xt, 4.35, f"{t.varo_egyseg:.0f}", ha="center", fontsize=7, color="#E07B39")
        if i < n - 1:
            ax.annotate("", xy=(x + 1.6, 3.1), xytext=(x + 1.0, 3.1), arrowprops=dict(arrowstyle="->", color="#285780"))
    xs, ys = [-0.3], [1.6]
    for i, t in d.iterrows():
        x = i * lx + 1.3
        xs += [x - 1.0, x - 1.0, x + 1.0, x + 1.0]; ys += [1.6, 0.9, 0.9, 1.6]
        ax.text(x - 1.3, 1.68, f"{t.varakozas_nap:.1f} nap", ha="center", fontsize=7.5, color="#E07B39")
        ax.text(x, 0.75, f"{t.muvelet_h:.2f} h", ha="center", va="top", fontsize=7.5, color="#285780")
    xs.append(n * lx); ys.append(1.6)
    ax.plot(xs, ys, color="#1F3A5A", lw=1.3)
    ax.text(n * lx + 0.3, 1.25, f"átfutás: {S['atf_nap']:.1f} nap\\nművelet: {S['muvelet']:.2f} h\\nhatékonyság: {S['pce']:.1%}",
            fontsize=8, va="center", bbox=dict(fc="#285780", ec="none", alpha=0.9), color="white")
    ax.set_xlim(-0.8, n * lx + 3.6); ax.set_ylim(0.2, 4.7); ax.axis("off")
    ax.set_title(cim, fontsize=10, loc="left")

fig = plt.figure(figsize=(14, 9.5))
gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1.1])
rajz_vsm(fig.add_subplot(gs[0, :]), jelen, S_j, "Jelenlegi állapot (a háromszögben a várakozó egységek száma)", kiemelt=int(jelen.varakozas_nap.idxmax()))
rajz_vsm(fig.add_subplot(gs[1, :]), jovo, S_f, "Jövőbeli állapot", kiemelt=int(jovo.varakozas_nap.idxmax()))
ax = fig.add_subplot(gs[2, 0])
y = np.arange(len(jelen))
ax.barh(y - 0.2, jelen.varakozas_nap, 0.4, color="#E07B39", label="jelenlegi")
ax.barh(y + 0.2, jovo.varakozas_nap, 0.4, color="#3E8E63", label="jövőbeli")
ax.set_yticks(y, [s.replace("-" + chr(10), "-").replace(chr(10), " ") for s in jelen.lepes], fontsize=8); ax.invert_yaxis()
ax.set_xlabel("várakozás a lépés előtt [nap]"); ax.legend(fontsize=8); ax.set_title("Hol csökken a várakozás?", fontsize=10)
ax = fig.add_subplot(gs[2, 1])
mut = ["átfutás [nap]", "műveleti idő [óra]", "folyamathatékonyság [%]"]
a = [S_j["atf_nap"], S_j["muvelet"], S_j["pce"] * 100]; b = [S_f["atf_nap"], S_f["muvelet"], S_f["pce"] * 100]
x = np.arange(3)
ax.bar(x - 0.2, a, 0.4, color="#E07B39", label="jelenlegi"); ax.bar(x + 0.2, b, 0.4, color="#3E8E63", label="jövőbeli")
for i in range(3):
    ax.text(x[i] - 0.2, a[i], f"{a[i]:.1f}", ha="center", va="bottom", fontsize=8)
    ax.text(x[i] + 0.2, b[i], f"{b[i]:.1f}", ha="center", va="bottom", fontsize=8)
ax.set_xticks(x, mut, fontsize=8); ax.legend(fontsize=8); ax.set_title("Mutatók", fontsize=10)
plt.tight_layout(); plt.savefig("folyamatabra_vsm.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A jelenlegi állapotban a rendelés 10 munkanapot (150 órát) tölt az üzemben, ebből a műveletek 5,8 órát tesznek ki: a folyamathatékonyság 3,9%. A Little-törvény (60 rendelés / napi 6) ugyanezt adja, a térkép tehát következetes.
- A leghosszabb várakozás a megmunkáló központ előtt van (3 nap); ez a szűk keresztmetszet. A második az anyag-előkészítés előtti várakozás (2,5 nap), amelyet az okoz, hogy az anyagbeszerzés csak a rendelés kiadása után indul.
- A jövőbeli állapotban a rendeléskiadás a megmunkáló központ kapacitásához kötött (legfeljebb 24 rendelés van folyamatban), az anyagot a kiadáskor lefoglalják, és a SMED-del rövidebb átállás kisebb sorozatokat enged. Az átfutás 4 napra csökken, a folyamathatékonyság 8,5%-ra nő. A műveleti idő alig változik: a nyereség szinte teljesen a várakozás csökkenéséből jön.
"""),
]
