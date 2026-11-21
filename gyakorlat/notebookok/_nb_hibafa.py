from _kozos import BETOLTO, code, fejresz, md

NEV = "hibafa"
CIM = "Hibafa: minimális vágathalmazok (MOCUS), pontos valószínűség, fontossági mértékek"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. a kapuk és az alapesemények táblázatából kiszámítja a minimális vágathalmazokat (MOCUS-algoritmus, Vesely és mtsai, 1981);
2. a csúcsesemény valószínűségét pontosan (az alapesemények összes állapotának felsorolásával), a vágathalmazokból és a kapuszintű, függetlenséget feltételező képletekkel is kiszámítja, és összeveti őket;
3. kiszámítja a Fussell–Vesely- és a Birnbaum-fontosságot: melyik alapesemény járul hozzá leginkább a kockázathoz, és melyik javítása csökkenti leginkább;
4. kirajzolja a hibafát.

A beépített példa a KoboCella biztonsági csúcseseménye; az E3 ismétlődő esemény (kézikönyv 16. fejezet).
""", sablon="hibafa_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Hibafa eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött hibafa_sablon.xlsx
''' + BETOLTO + '''
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("hibafa_sablon.xlsx")
    a = pd.read_excel(fajl, sheet_name="Alapesemények", header=2).iloc[:, :3].dropna(subset=[0] if False else None)
    a = a[a.iloc[:, 0].notna() & a.iloc[:, 2].notna()]
    p = dict(zip(a.iloc[:, 0].astype(str), a.iloc[:, 2].astype(float)))
    leiras = dict(zip(a.iloc[:, 0].astype(str), a.iloc[:, 1].astype(str)))
    k = pd.read_excel(fajl, sheet_name="Kapuk", header=3).iloc[:, :8]
    k = k[k.iloc[:, 0].notna() & k.iloc[:, 2].notna()]
    kapuk = {str(r.iloc[0]): (str(r.iloc[2]), [str(x) for x in r.iloc[3:8] if pd.notna(x)]) for _, r in k.iterrows()}
    leiras.update({str(r.iloc[0]): str(r.iloc[1]) for _, r in k.iterrows()})
    csucs = str(k.iloc[0, 0])
else:
    p = {"E1": 0.3, "E2": 0.01, "E3": 0.001, "E4": 0.005}
    leiras = {"E1": "kezelő a közös térben", "E2": "a szkenner nem érzékel", "E3": "a biztonsági vezérlés hibája",
              "E4": "az erőhatárolás hibája", "G1": "teljes sebességű ütközés", "G2": "nincs sebességcsökkentés", "G3": "nincs erőhatárolás"}
    kapuk = {"G1": ("ÉS", ["E1", "G2", "G3"]), "G2": ("VAGY", ["E2", "E3"]), "G3": ("VAGY", ["E4", "E3"])}
    csucs = "G1"
alap = sorted(p)
print(f"{len(alap)} alapesemény, {len(kapuk)} kapu, csúcsesemény: {csucs} ({leiras.get(csucs, '')})")
'''),
    md("## Minimális vágathalmazok (MOCUS)"),
    code('''
def mocus(csucs):
    halmazok = [[csucs]]
    valtozott = True
    while valtozott:
        valtozott = False
        uj = []
        for h in halmazok:
            kapu = next((x for x in h if x in kapuk), None)
            if kapu is None:
                uj.append(h); continue
            valtozott = True
            tipus, be = kapuk[kapu]
            maradek = [x for x in h if x != kapu]
            if tipus == "ÉS":
                uj.append(maradek + be)
            else:
                uj.extend(maradek + [b] for b in be)
        halmazok = uj
    halmazok = [frozenset(h) for h in halmazok]
    minimalis = [h for h in set(halmazok) if not any(m < h for m in halmazok)]
    return sorted(minimalis, key=lambda h: (len(h), sorted(h)))

vagatok = mocus(csucs)
for h in vagatok:
    print("{" + ", ".join(sorted(h)) + "}", f"P = {np.prod([p[e] for e in h]):.3e}", "  <- egypontos hiba" if len(h) == 1 else "")
ismetlodo = [e for e in alap if sum(e in be for _, be in kapuk.values()) > 1]
print("Ismétlődő alapesemények:", ismetlodo or "nincs")
'''),
    md("## Valószínűségek és fontosság"),
    code('''
def kapu_ertek(x, allapot):
    if x not in kapuk:
        return allapot[x]
    tipus, be = kapuk[x]
    v = [kapu_ertek(b, allapot) for b in be]
    return all(v) if tipus == "ÉS" else any(v)

def pontos(pp):
    ossz = 0.0
    for bitek in itertools.product([0, 1], repeat=len(alap)):
        allapot = dict(zip(alap, bitek))
        if kapu_ertek(csucs, allapot):
            ossz += np.prod([pp[e] if allapot[e] else 1 - pp[e] for e in alap])
    return ossz

def naiv(x):
    if x not in kapuk:
        return p[x]
    tipus, be = kapuk[x]
    v = np.array([naiv(b) for b in be])
    return v.prod() if tipus == "ÉS" else 1 - (1 - v).prod()

P_pontos = pontos(p)
P_ritka = sum(np.prod([p[e] for e in h]) for h in vagatok)
P_naiv = naiv(csucs)
print(f"Pontos: {P_pontos:.4e}; vágathalmazokból (ritka esemény közelítés): {P_ritka:.4e}; kapuszintű (független): {P_naiv:.4e}")
print(f"A kapuszintű számítás {P_pontos / P_naiv:.1f}-szeresen alábecsül.")

fv = {e: sum(np.prod([p[x] for x in h]) for h in vagatok if e in h) / P_ritka for e in alap}
birn = {e: pontos({**p, e: 1.0}) - pontos({**p, e: 0.0}) for e in alap}
fontossag = pd.DataFrame({"leírás": [leiras.get(e, "") for e in alap], "p": [p[e] for e in alap],
                          "Fussell–Vesely": [fv[e] for e in alap], "Birnbaum": [birn[e] for e in alap]}, index=alap)
fontossag
'''),
    md("## Ábra"),
    code('''
def elrendez(x, melyseg=0, poz=None, szamlalo=None):
    if poz is None:
        poz, szamlalo = {}, [0]
    if x in kapuk:
        gy = [elrendez(b, melyseg + 1, poz, szamlalo) for b in kapuk[x][1]]
        poz.setdefault(x, (np.mean([g[0] for g in gy]), -melyseg))
    else:
        poz.setdefault(x, (szamlalo[0], -melyseg)); szamlalo[0] += 1
    return poz[x]

poz = {}
elrendez(csucs, 0, poz, [0])
fig, axs = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={"width_ratios": [1.4, 1]})
ax = axs[0]
for g, (tipus, be) in kapuk.items():
    for b in be:
        ax.plot([poz[g][0], poz[b][0]], [poz[g][1], poz[b][1]], color="#999999", lw=1, zorder=1)
for x, (px, py) in poz.items():
    if x in kapuk:
        ax.add_patch(plt.Rectangle((px - 0.45, py - 0.18), 0.9, 0.36, color="#285780", zorder=2))
        ax.text(px, py, f"{x} {kapuk[x][0]}", color="white", ha="center", va="center", fontsize=8, zorder=3)
        ax.text(px, py + 0.25, leiras.get(x, ""), ha="center", fontsize=7)
    else:
        szin = "#E07B39" if x in ismetlodo else "#A9C4DE"
        ax.add_patch(plt.Circle((px, py), 0.22, color=szin, zorder=2))
        ax.text(px, py, x, ha="center", va="center", fontsize=8, zorder=3)
        ax.text(px, py - 0.35, f"{leiras.get(x, '')}\\np = {p[x]:g}", ha="center", va="top", fontsize=7)
ax.set_xlim(-0.8, max(v[0] for v in poz.values()) + 0.8); ax.set_ylim(min(v[1] for v in poz.values()) - 0.9, 0.6)
ax.axis("off"); ax.set_title("A hibafa (narancs: ismétlődő esemény)", fontsize=10)
ax = axs[1]
y = np.arange(len(alap))
ax.barh(y - 0.2, fontossag["Fussell–Vesely"], 0.4, color="#285780", label="Fussell–Vesely (hozzájárulás)")
ax2 = ax.twiny()
ax2.barh(y + 0.2, fontossag["Birnbaum"], 0.4, color="#E07B39", label="Birnbaum (érzékenység)")
ax.set_yticks(y); ax.set_yticklabels([f"{e}" for e in alap]); ax.invert_yaxis()
ax.set_xlabel("Fussell–Vesely"); ax2.set_xlabel("Birnbaum")
ax.legend(loc="lower right", fontsize=8); ax2.legend(loc="lower right", fontsize=8, bbox_to_anchor=(1, 0.1))
ax.set_title(f"Fontosság; P(csúcs) pontos = {P_pontos:.2e}, kapuszintű = {P_naiv:.2e}", fontsize=9, pad=28)
plt.tight_layout(); plt.savefig("hibafa_elemzes.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A KoboCella hibafájának két minimális vágathalmaza van: {E1, E3} és {E1, E2, E4}. Egypontos hiba nincs, de az első vágathalmaz csak egy technikai eseményt (a biztonsági vezérlés hibáját) tartalmaz a kezelő jelenléte mellett, és a kockázat mintegy 95%-át adja.
- A kapuszintű számítás az ismétlődő E3 miatt mintegy tizenhatszor kisebb valószínűséget ad, mint a pontos: a hibát mindig az optimista irányba követi el.
- A fontossági mértékek megmutatják, hova érdemes beruházni. Az E1 (a kezelő jelenléte) minden vágathalmazban szerepel, ezért Fussell–Vesely-fontossága 1; ez a feltétel a cella működésének része, nem javítandó hiba. A technikai események közül az E3 Fussell–Vesely-fontossága (kb. 0,95) és Birnbaum-fontossága is messze a legnagyobb: ennek javítása csökkenti leginkább a csúcsesemény valószínűségét. Ezért tervezte a csapat a két védelmi funkciót független csatornára.
"""),
]
