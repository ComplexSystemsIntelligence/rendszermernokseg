from _kozos import BETOLTO, code, fejresz, md

NEV = "kapacitas"
CIM = "Kapacitás, szűk keresztmetszet, kihasználtság és munkaerő-termelékenység; változatok és több terméktípus"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. kiszámítja az erőforrások kapacitását, a szűk keresztmetszetet, az áramot és a kihasználtságot;
2. kiszámítja a munkatartalmat, a ciklusidőt, a kihasználatlan időt, az átlagos munkaerő-kihasználtságot és az egységnyi munkaerőköltséget;
3. összeveti az alapállapotot egy változattal (például csúcsidőszak, átcsoportosított feladatok);
4. több terméktípusnál a származtatott kihasználtsággal keresi a szűk keresztmetszetet;
5. megmutatja, hogyan változik az áram a kereslettel, és mit érne egy-egy erőforrás bővítése.

A beépített példa a VárosiBringa javítóműhelye (kézikönyv 19. fejezet; Cachon és Terwiesch, 2013, 3–4. fejezet).
""", sablon="kapacitas_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Kapacitás és szűk keresztmetszet eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött kapacitas_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
def lap_olvas(fajl, lap):
    p = pd.read_excel(fajl, sheet_name=lap, header=None, nrows=6)
    d = pd.read_excel(fajl, sheet_name=lap, header=7).iloc[:, :4]
    d.columns = ["eroforras", "tipus", "m", "p"]
    d = d[d.eroforras.notna() & d.p.notna()].reset_index(drop=True)
    return dict(napi=float(p.iloc[2, 1]), ora=float(p.iloc[3, 1]), ber=float(p.iloc[4, 1]), t=d)

if SAJAT_SABLON:
    fajl = sablon_betoltese("kapacitas_sablon.xlsx")
    alap, valt = lap_olvas(fajl, "Alap"), lap_olvas(fajl, "Változat")
    tp = pd.read_excel(fajl, sheet_name="Többtermékes", header=None)
    ORA_T = float(tp.iloc[2, 1])
    termekek = [(str(tp.iloc[4, 3 + j]), float(tp.iloc[5, 3 + j])) for j in range(4) if pd.notna(tp.iloc[4, 3 + j]) and pd.notna(tp.iloc[5, 3 + j])]
    tt = tp.iloc[8:, :7].copy(); tt.columns = ["eroforras", "m", "rend", "p1", "p2", "p3", "p4"]
    tt = tt[tt.eroforras.notna() & pd.to_numeric(tt.m, errors="coerce").notna() & pd.to_numeric(tt.rend, errors="coerce").notna()].reset_index(drop=True)
    tobb = pd.DataFrame({"eroforras": tt.eroforras, "m": tt.m.astype(float)})
    for j, (nev, _) in enumerate(termekek):
        tobb[nev] = pd.to_numeric(tt[f"p{j + 1}"], errors="coerce").fillna(0)
else:
    t0 = pd.DataFrame({"eroforras": ["átvétel, diagnosztika", "mosás", "fékjavítás", "hajtáslánc-javítás", "végellenőrzés"],
                       "tipus": ["dolgozó"] * 5, "m": [1, 1, 2, 1, 1], "p": [6, 4, 14, 9, 5]})
    alap = dict(napi=40, ora=7.5, ber=4000, t=t0)
    t1 = t0.copy(); t1.loc[1, "eroforras"] = "mosás (+ lánctisztítás)"; t1.loc[1, "p"] = 7; t1.loc[3, "p"] = 6
    valt = dict(napi=55, ora=7.5, ber=4000, t=t1)
    ORA_T = 7.5
    termekek = [("hagyományos", 30), ("elektromos", 10)]
    tobb = pd.DataFrame({"eroforras": t0.eroforras, "m": t0.m, "hagyományos": [5, 4, 13, 8, 4.5], "elektromos": [9, 4, 17, 12, 6.5]})

def ezres(x):
    return f"{x:,.0f}".replace(",", " ")

def elemez(e, nev):
    t = e["t"].copy()
    D = e["napi"] / e["ora"]
    t["kap"] = 60 * t.m / t.p
    K = t.kap.min(); R = min(D, K); CT = 60 / R
    t["kihaszn"] = R / t.kap
    dolg = t.tipus == "dolgozó"
    munkatartalom = t.loc[dolg, "p"].sum(); letszam = t.loc[dolg, "m"].sum()
    t["kihasznalatlan"] = np.where(dolg, t.m * CT - t.p, np.nan)
    u_munka = munkatartalom / (CT * letszam)
    koltseg = letszam * e["ber"] / R
    szk = t.eroforras[t.kap == K].tolist()
    print(f"{nev}: kereslet {D:.2f}/óra, kapacitás {K:.2f}/óra ({' és '.join(szk)}), áram {R:.2f}/óra "
          f"({'kapacitáskorlátos' if D > K else 'keresletkorlátos'}), napi {R * e['ora']:.0f} egység")
    print(f"   ciklusidő {CT:.2f} perc, munkatartalom {munkatartalom:.0f} perc, létszám {letszam:.0f}, "
          f"kihasználatlan idő {t.kihasznalatlan.sum():.1f} perc/ciklus, munkaerő-kihasználtság {u_munka:.1%}, "
          f"munkaerőköltség {ezres(koltseg)} Ft/egység (a munkatartalomé {ezres(munkatartalom / 60 * e['ber'])} Ft)")
    print(t[["eroforras", "m", "p", "kap", "kihaszn"]].round(3).to_string(index=False))
    return dict(t=t, D=D, K=K, R=R, CT=CT, u=u_munka)

A = elemez(alap, "Alapállapot")
V = elemez(valt, "Változat  ")
# mi lenne, ha a változat feladatátcsoportosítása nélkül jönne a csúcs?
csucs_atcs_nelkul = dict(alap, napi=valt["napi"])
_ = elemez(csucs_atcs_nelkul, "Csúcs átcsoportosítás nélkül")
'''),
    md("## Több terméktípus: származtatott kihasználtság"),
    code('''
igeny = sum(tobb[nev] * d for nev, d in termekek)
rendelk = tobb.m * ORA_T * 60
tobb["szarm_kihaszn"] = igeny / rendelk
szk_t = tobb.loc[tobb.szarm_kihaszn.idxmax(), "eroforras"]
osszes = sum(d for _, d in termekek)
print(tobb.round(3).to_string(index=False))
print(f"Szűk keresztmetszet: {szk_t} ({tobb.szarm_kihaszn.max():.1%}); legnagyobb napi kibocsátás változatlan összetétellel: "
      f"{osszes / tobb.szarm_kihaszn.max():.1f} egység")
# érzékenység: hogyan változik a szűk keresztmetszet, ha nő az elektromos kerékpárok aránya?
aranyok = np.linspace(0, 1, 11)
max_kib = []
for a in aranyok:
    p_atl = (1 - a) * tobb[termekek[0][0]] + a * tobb[termekek[-1][0]]
    max_kib.append((tobb.m * ORA_T * 60 / p_atl).min())
print("A legnagyobb napi kibocsátás a(z)", termekek[-1][0], "arány függvényében:",
      {f"{a:.0%}": round(float(k), 1) for a, k in zip(aranyok, max_kib)})
'''),
    md("## Ábra"),
    code('''
fig, axs = plt.subplots(1, 3, figsize=(16, 4.6))
ax = axs[0]
y = np.arange(len(A["t"]))
ax.barh(y - 0.2, A["t"].kihaszn * 100, 0.4, color="#285780", label=f"alapállapot (napi {alap['napi']:.0f})")
ax.barh(y + 0.2, V["t"].kihaszn * 100, 0.4, color="#E07B39", label=f"változat (napi {valt['napi']:.0f})")
ax.set_yticks(y, V["t"].eroforras, fontsize=8); ax.invert_yaxis()
ax.axvline(100, color="#B83A3A", ls="--"); ax.set_xlabel("kihasználtság [%]"); ax.legend(fontsize=8, loc="lower right")
ax.set_title("Kihasználtság erőforrásonként", fontsize=10)
ax = axs[1]
d = np.linspace(0, 1.6 * A["K"], 200)
ax.plot(d, np.minimum(d, A["K"]), color="#285780", label="alapállapot")
ax.plot(d, np.minimum(d, V["t"].kap.min()), color="#E07B39", ls="--", label="változat")
for e, c in ((alap, "#285780"), (valt, "#E07B39")):
    ax.axvline(e["napi"] / e["ora"], color=c, ls=":", lw=1)
ax.set_xlabel("kereslet [egység/óra]"); ax.set_ylabel("áram [egység/óra]"); ax.legend(fontsize=8)
ax.set_title("Áram a kereslet függvényében", fontsize=10); ax.grid(alpha=0.3)
ax = axs[2]
ax.plot(np.array(aranyok) * 100, max_kib, "o-", color="#3E8E63")
jelen = termekek[-1][1] / osszes * 100
ax.axvline(jelen, color="#999999", ls=":"); ax.text(jelen + 1, min(max_kib), "jelenlegi arány", fontsize=8)
ax.axhline(osszes, color="#B83A3A", ls="--", lw=1); ax.text(1, osszes + 0.5, "jelenlegi kereslet", fontsize=8, color="#B83A3A")
ax.set_xlabel(f"{termekek[-1][0]} termékek aránya [%]"); ax.set_ylabel("legnagyobb kibocsátás [egység/nap]")
ax.set_title("Termékösszetétel és kapacitás", fontsize=10); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("kapacitas.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- Az alapállapotban a szűk keresztmetszet a hajtáslánc-javítás (6,7 kerékpár/óra, napi 50); a folyamat keresletkorlátos, a szűk keresztmetszet kihasználtsága 80%, a munkaerő-kihasználtság 56,3%.
- A napi 55 kerékpáros csúcsot az alapállapot nem tudná kiszolgálni (kapacitáskorlátos lenne), egy második mosó semmit nem segítene. A lánctisztítás átcsoportosítása után a szűk keresztmetszet a mosás és a fékjavítás 8,6 kerékpár/órával, a csúcsigény kiszolgálható, a munkaerő-kihasználtság 77%-ra nő, az egységnyi munkaerőköltség csökken.
- A 86%-os kihasználtság mellett azonban a változékonyság miatt a várakozás már jelentős lehet (kézikönyv 21. fejezet: sorbanállás).
- Több terméktípusnál a szűk keresztmetszet a termékösszetételtől függ: minél több az elektromos kerékpár, annál kisebb a legnagyobb napi kibocsátás.
"""),
]
