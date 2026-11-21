from _kozos import BETOLTO, code, fejresz, md

NEV = "sorbanallas"
CIM = "Sorbanállás: M/M/c pontosan, G/G/c közelítés, diszkrét eseményű szimuláció és napon belüli sorok"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. kiszámítja az M/M/c rendszer pontos jellemzőit (Erlang C) és a Hopp–Spearman-féle G/G/c közelítést, és összeveti őket;
2. megrajzolja a várakozást a kihasználtság függvényében különböző változékonyságnál;
3. diszkrét eseményű szimulációval modellezi a teljes javítóműhelyt (öt egymást követő munkahely), és összeveti az eredményt a képletekkel;
4. megmutatja, hogyan alakul a sor egy napon belül, ha a kerékpárok reggel sűrűbben érkeznek.

A beépített példa a VárosiBringa javítóműhelye (kézikönyv 19. és 21. fejezet; Kendall, 1953; Kingman, 1961; Hopp és Spearman, 2008; Law, 2015).
""", sablon="sorbanallas_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Sorbanállási modellek eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött sorbanallas_sablon.xlsx (Változatok lap)
NAPOK = 400            # szimulált napok száma
''' + BETOLTO + '''
import heapq
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Képletek"),
    code('''
def mmc(lam, ts, c):
    """M/M/c pontos jellemzői; lam [1/óra], ts [perc]. Visszaad: rho, Pw, Wq [perc], Lq."""
    mu = 60 / ts; a = lam / mu; rho = a / c
    if rho >= 1: return dict(rho=rho, Pw=np.nan, Wq=np.inf, Lq=np.inf)
    s = sum(a ** k / math.factorial(k) for k in range(c))
    p0 = 1 / (s + a ** c / (math.factorial(c) * (1 - rho)))
    pw = a ** c / (math.factorial(c) * (1 - rho)) * p0
    lq = pw * rho / (1 - rho)
    return dict(rho=rho, Pw=pw, Wq=lq / lam * 60, Lq=lq)

def ggc(lam, ts, c, ca, cs):
    """Hopp–Spearman G/G/c közelítés; Wq [perc]."""
    rho = lam * ts / 60 / c
    if rho >= 1: return np.inf
    return (ca ** 2 + cs ** 2) / 2 * rho ** (math.sqrt(2 * (c + 1)) - 1) / (c * (1 - rho)) * ts

if SAJAT_SABLON:
    fajl = sablon_betoltese("sorbanallas_sablon.xlsx")
    v = pd.read_excel(fajl, sheet_name="Változatok", header=2).iloc[:20, :6]
    v.columns = ["nev", "lam", "ts", "c", "ca", "cs"]
    valt = v[v.nev.notna() & pd.to_numeric(v.lam, errors="coerce").notna()].reset_index(drop=True)
else:
    valt = pd.DataFrame([("hajtáslánc, alapállapot (M/M/1)", 40 / 7.5, 9, 1, 1, 1), ("hajtáslánc, mért kiszolgálási szórás", 40 / 7.5, 9, 1, 1, 0.5),
                         ("fékjavítás, alapállapot (2 szerelő)", 40 / 7.5, 14, 2, 1, 1), ("mosás + lánctisztítás, nyári csúcs", 55 / 7.5, 7, 1, 1, 1),
                         ("fékjavítás, nyári csúcs", 55 / 7.5, 14, 2, 1, 1), ("mosás, csúcs, időpontfoglalással", 55 / 7.5, 7, 1, 0.5, 0.5)],
                        columns=["nev", "lam", "ts", "c", "ca", "cs"])
valt[["lam", "ts", "ca", "cs"]] = valt[["lam", "ts", "ca", "cs"]].astype(float); valt["c"] = valt.c.astype(int)
sor = []
for r in valt.itertuples():
    e = mmc(r.lam, r.ts, r.c)
    sor.append(dict(változat=r.nev, rho=round(e["rho"], 3), Wq_MMc_pontos=round(e["Wq"], 1),
                    Wq_GGc_közelítés=round(ggc(r.lam, r.ts, r.c, r.ca, r.cs), 1), várakozás_valószínűsége=round(e["Pw"], 2)))
print(pd.DataFrame(sor).to_string(index=False))
print("(Az M/M/c oszlop a ca = cs = 1 esetre vonatkozik; a közelítés oszlop a megadott változékonysággal számol.)")
'''),
    md("## Diszkrét eseményű szimuláció: a teljes műhely"),
    code('''
ALLOMAS = [("átvétel, diagnosztika", 1, 6), ("mosás", 1, 4), ("fékjavítás", 2, 14), ("hajtáslánc", 1, 9), ("végellenőrzés", 1, 5)]
CS = 0.5          # a javítási idők relatív szórása (mért érték)
NAP_PERC = 450    # nyitvatartás percben

def javido(rng, m, cs):
    s = math.sqrt(math.log(1 + cs ** 2))
    return rng.lognormal(math.log(m) - s ** 2 / 2, s)

def szimulal(erkezesi_profil, napok, allomas, cs, seed=1):
    """Napi érkezések (perc) listája → minden állomásra a várakozási idők és a sorhossz időbeli lefolyása."""
    rng = np.random.default_rng(seed)
    var = {k: [] for k in range(len(allomas))}
    sorhossz = []   # (napon belüli idő, állomás, sorhossz)
    for nap in range(napok):
        erk = erkezesi_profil(rng)
        esem = [(t, 0, i, 0) for i, t in enumerate(erk)]   # (idő, állomás, kerékpár, típus 0 = érkezés)
        heapq.heapify(esem)
        szabad = [c for _, c, _ in allomas]
        sorok = [[] for _ in allomas]
        while esem:
            t, k, i, tip = heapq.heappop(esem)
            if tip == 0:                       # érkezés a k. állomásra
                if szabad[k] > 0:
                    szabad[k] -= 1; var[k].append(0.0)
                    heapq.heappush(esem, (t + javido(rng, allomas[k][2], cs), k, i, 1))
                else:
                    sorok[k].append((t, i))
            else:                              # befejezés a k. állomáson
                if k + 1 < len(allomas):
                    heapq.heappush(esem, (t, k + 1, i, 0))
                if sorok[k]:
                    t0, j = sorok[k].pop(0); var[k].append(t - t0)
                    heapq.heappush(esem, (t + javido(rng, allomas[k][2], cs), k, j, 1))
                else:
                    szabad[k] += 1
            if nap < 60:
                sorhossz.append((t, k, len(sorok[k])))
    return var, pd.DataFrame(sorhossz, columns=["t", "allomas", "sor"])

def egyenletes(napi):
    return lambda rng: np.sort(rng.uniform(0, NAP_PERC, rng.poisson(napi)))

def reggeli_csucs(napi, arany=0.6, csucs_vege=180):
    def f(rng):
        n = rng.poisson(napi); n1 = rng.binomial(n, arany)
        return np.sort(np.concatenate([rng.uniform(0, csucs_vege, n1), rng.uniform(csucs_vege, NAP_PERC, n - n1)]))
    return f

eredm = {}
for nev, prof in (("egyenletes, napi 40", egyenletes(40)), ("reggeli csúcs, napi 40", reggeli_csucs(40))):
    var, sh = szimulal(prof, NAPOK, ALLOMAS, CS)
    eredm[nev] = (var, sh)
    print(f"{nev}: átlagos várakozás állomásonként [perc]:",
          {ALLOMAS[k][0]: round(float(np.mean(v)), 1) for k, v in var.items()})
lam = 40 / 7.5
print("G/G/c közelítés (ca = 1, cs = 0,5), egyenletes érkezésre [perc]:",
      {n: round(ggc(lam, ts, c, 1, CS), 1) for n, c, ts in ALLOMAS})
'''),
    md("## Ábra"),
    code('''
fig, axs = plt.subplots(1, 3, figsize=(17, 4.8))
ax = axs[0]
rho = np.linspace(0.05, 0.97, 200)
for c, cs, st in ((1, 1, "-"), (1, 0.5, "--"), (2, 1, "-.")):
    ax.plot(rho, [ggc(r * c * 60 / 9, 9, c, 1, cs) / 9 for r in rho], st, label=f"c = {c}, cs = {cs}", lw=2)
ax.plot(rho, [mmc(r * 2 * 60 / 9, 9, 2)["Wq"] / 9 for r in rho], ":", color="#555555", label="M/M/2 pontos")
ax.set_ylim(0, 15); ax.set_xlabel("kihasználtság ρ"); ax.set_ylabel("Wq / ts"); ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax.set_title("Várakozás a kihasználtság függvényében", fontsize=10)
ax = axs[1]
x = np.arange(len(ALLOMAS))
sim_e = [np.mean(eredm["egyenletes, napi 40"][0][k]) for k in range(len(ALLOMAS))]
sim_r = [np.mean(eredm["reggeli csúcs, napi 40"][0][k]) for k in range(len(ALLOMAS))]
kozel = [ggc(lam, ts, c, 1, CS) for _, c, ts in ALLOMAS]
ax.bar(x - 0.27, kozel, 0.27, color="#A9C4DE", label="közelítés (stacionárius)")
ax.bar(x, sim_e, 0.27, color="#285780", label="szimuláció, egyenletes érkezés")
ax.bar(x + 0.27, sim_r, 0.27, color="#E07B39", label="szimuláció, reggeli csúcs")
ax.set_xticks(x, [a[0] for a in ALLOMAS], rotation=20, fontsize=8); ax.set_ylabel("átlagos várakozás [perc]")
ax.legend(fontsize=8); ax.set_title("Képlet és szimuláció a műhely öt munkahelyén", fontsize=10)
ax = axs[2]
for nev, c in (("egyenletes, napi 40", "#285780"), ("reggeli csúcs, napi 40", "#E07B39")):
    sh = eredm[nev][1]
    h = sh[sh.allomas == 3].copy()
    h["sav"] = (h.t // 30) * 30
    g = h.groupby("sav").sor.mean()
    ax.plot(g.index / 60, g.values, "o-", color=c, label=nev, ms=3)
ax.set_xlabel("idő a nyitástól [óra]"); ax.set_ylabel("átlagos sorhossz a hajtásláncnál"); ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax.set_title("A sor napon belüli alakulása (hajtáslánc)", fontsize=10)
plt.tight_layout(); plt.savefig("sorbanallas.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A hajtásláncnál 80%-os kihasználtság mellett exponenciális javítási időkkel 36 perc, a mért 0,5-ös relatív szórással 22,5 perc a várható várakozás. A két szerelős fékjavításnál a közelítés (9,3 perc) jól egyezik az M/M/2 pontos értékével (8,8 perc).
- A nyári csúcsban a mosás és a fékjavítás 86%-os kihasználtsággal dolgozik; a várakozás 40 perc körülire nő. Időpontfoglalással (kisebb érkezési szórás) és szabványos munkával a mosásnál 10 perc körülire csökken.
- A szimuláció a műhely egészét modellezi. A szűk keresztmetszet (hajtáslánc) átlagos várakozása egyenletes érkezésnél mintegy 13 perc, kisebb a stacionárius képlet 22,5 percénél: a műhely minden reggel üresen nyit, a napi 7,5 óra alatt a sor nem éri el a hosszú távú átlagot, és a megelőző munkahelyek kisimítják az érkezéseket. Ha a kerékpárok 60%-a az első három órában érkezik, a sor délelőtt felhalmozódik, és a hajtásláncnál a várakozás csaknem kétszeresére nő. Ilyen napon belüli hatásokat a stacionárius képletek nem mutatnak: ezekhez szimuláció kell.
"""),
]
