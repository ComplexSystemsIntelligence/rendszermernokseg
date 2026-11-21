from _kozos import BETOLTO, code, fejresz, md

NEV = "morfologiai_doboz"
CIM = "Morfológiai doboz: kombinációk, összeférhetőség, változatos koncepciók"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook egy morfológiai dobozból

1. megszámolja az elvi kombinációkat, majd az összeférhetetlen párok és a kizárt részmegoldások figyelembevételével a megmaradó kombinációkat;
2. megmutatja, hogy az egyes részmegoldások a megmaradó kombinációk hányadában fordulnak elő (melyik megoldás „zár ki” sok mindent);
3. ellenőrzi a megadott koncepciók összeférhetőségét, és **változatossági szempont** szerint további koncepciókat javasol: olyanokat, amelyek a lehető legtöbb részfunkcióban különböznek a már kiválasztottaktól.

A beépített példa a KoboCella morfológiai doboza (kézikönyv 9. fejezet).
""", sablon="morfologiai_doboz_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Morfológiai doboz eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött morfologiai_doboz_sablon.xlsx
KIZART = ["F4.1"]      # kötelező követelmény miatt kizárt részmegoldások (itt: R-09 – minden kötés adata kell)
JAVASOLT_UJ = 2        # hány további, változatos koncepciót javasoljon
''' + BETOLTO + '''
import itertools
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("morfologiai_doboz_sablon.xlsx")
    d = pd.read_excel(fajl, sheet_name="Doboz", header=3).dropna(subset=["Kód", "Részfunkció"])
    funkciok = [(r["Kód"], r["Részfunkció"], [v for v in r.iloc[2:8] if isinstance(v, str)]) for _, r in d.iterrows()]
    o = pd.read_excel(fajl, sheet_name="Összeférhetetlen", header=3)
    tiltott = {frozenset((a.strip(), b.strip())) for a, b in zip(o.iloc[:, 0], o.iloc[:, 1])
               if isinstance(a, str) and isinstance(b, str) and "." in a}
    koncepciok = {}
else:
    funkciok = [
        ("F1", "motorház befogása", ["kézi befogó", "pneumatikus befogó", "forgóasztal két befogóval", "robot tartja"]),
        ("F2", "csavar adagolása", ["kézi, tálcából", "rezgőadagoló + tömlő", "szívófejes kiemelés", "előre töltött tár"]),
        ("F3", "csavar meghúzása", ["kézi csavarbehajtó", "kobot + egyorsós fej", "többorsós fix fej", "ipari robot zárt cellában"]),
        ("F4", "nyomaték mérése", ["nyomatékkulcs mintavétellel", "orsóba épített mérés", "külső mérőállomás", "áramfelvételből becsült"]),
        ("F5", "védőzóna figyelése", ["fix védőrács", "fényfüggöny", "lézerszkenner + sebességkorlát", "erő- és teljesítménykorlátozás"]),
        ("F6", "kész motor kivétele", ["kézi kivétel", "kobot a kiadóba", "szállítószalag", "gravitációs csúszda"])]
    parok = [("F3.1", "F2.3"), ("F3.1", "F5.1"), ("F3.1", "F5.3"), ("F3.1", "F5.4"), ("F3.1", "F1.4"), ("F3.1", "F6.2"),
             ("F3.2", "F5.1"), ("F3.3", "F1.4"), ("F3.3", "F2.1"), ("F3.3", "F5.4"), ("F3.3", "F6.2"), ("F3.4", "F1.1"),
             ("F3.4", "F2.1"), ("F3.4", "F5.3"), ("F3.4", "F5.4"), ("F3.4", "F6.1"), ("F3.4", "F6.2")]
    tiltott = {frozenset(p) for p in parok}
    koncepciok = {"A – együttműködő cella": ["F1.2", "F2.2", "F3.2", "F4.2", "F5.3", "F6.2"],
                  "B – fix állomás": ["F1.3", "F2.4", "F3.3", "F4.2", "F5.1", "F6.3"]}
kodok = [[f"{k}.{j + 1}" for j in range(len(op))] for k, _, op in funkciok]
megoldas = {f"{k}.{j + 1}": o for k, _, op in funkciok for j, o in enumerate(op)}
print("Részfunkciók és megoldásszámok:", [(k, len(op)) for k, _, op in funkciok])
'''),
    md("## Kombinációk megszámlálása"),
    code('''
def osszefero(komb):
    return not any(frozenset(p) in tiltott for p in itertools.combinations(komb, 2))

elvi = int(np.prod([len(k) for k in kodok]))
osszefero_komb = [c for c in itertools.product(*kodok) if osszefero(c)]
megmarado = [c for c in osszefero_komb if not set(c) & set(KIZART)]
print(f"Elvi kombinációk: {elvi}")
print(f"Összeférhető kombinációk ({len(tiltott)} tiltott pár után): {len(osszefero_komb)}")
print(f"A kizárt részmegoldások ({', '.join(KIZART) or 'nincs'}) nélkül: {len(megmarado)}")
'''),
    md("## Melyik részmegoldás mennyire korlátoz?"),
    code('''
gyak = pd.DataFrame(np.nan, index=[f"{k} {n}" for k, n, _ in funkciok], columns=[f"{j + 1}." for j in range(max(map(len, kodok)))])
for i, ks in enumerate(kodok):
    for j, k in enumerate(ks):
        gyak.iat[i, j] = 100 * sum(k in c for c in megmarado) / max(1, len(megmarado))
fig, ax = plt.subplots(figsize=(12, 5.2))
im = ax.imshow(gyak.to_numpy(), cmap="Blues", vmin=0, vmax=max(60, np.nanmax(gyak.to_numpy())), aspect="auto")
for i in range(gyak.shape[0]):
    for j in range(gyak.shape[1]):
        v = gyak.iat[i, j]
        if not np.isnan(v):
            ax.text(j, i, textwrap.fill(megoldas[kodok[i][j]], 18) + f"\\n{v:.0f}%", ha="center", va="center", fontsize=7.5,
                    color="white" if v > 35 else "black")
ax.set_xticks(range(gyak.shape[1]), gyak.columns); ax.set_yticks(range(gyak.shape[0]), gyak.index, fontsize=8)
ax.set_title("A részmegoldások előfordulása a megmaradó kombinációkban", fontsize=10)
plt.colorbar(im, ax=ax, label="%"); plt.tight_layout()
plt.savefig("morf_gyakorisag.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("## Koncepciók ellenőrzése és változatos új koncepciók javaslata"),
    code('''
for nev_, k in koncepciok.items():
    hibak = [tuple(p) for p in itertools.combinations(k, 2) if frozenset(p) in tiltott]
    print(f"{nev_}: {'összeférhető' if not hibak else 'ÖSSZEFÉRHETETLEN: ' + str(hibak)}")

kivalasztott = [tuple(k) for k in koncepciok.values()]
def tavolsag(a, b):
    return sum(x != y for x, y in zip(a, b))
javaslatok = []
for _ in range(JAVASOLT_UJ):
    jelolt = max(megmarado, key=lambda c: (min([tavolsag(c, s) for s in kivalasztott] or [len(c)]), c))
    kivalasztott.append(jelolt); javaslatok.append(jelolt)
tabla = pd.DataFrame({f"javaslat {i + 1}": [megoldas[x] for x in c] for i, c in enumerate(javaslatok)},
                     index=[f"{k} {n}" for k, n, _ in funkciok])
for nev_, k in koncepciok.items():
    tabla.insert(0, nev_, [megoldas[x] for x in k])
tabla
'''),
    md("""
## Értelmezés

- A KoboCella dobozában a 4096 elvi kombinációból 1344 összeférhető, és a mintavételes nyomatékellenőrzés (F4.1) kizárása után 1008 marad. Ennyi koncepciót nem lehet egyenként értékelni: néhány jellegzetes, egymástól jól különböző koncepciót kell kiválasztani.
- A gyakorisági ábra megmutatja, mely részmegoldások maradnak a legtöbb kombinációban (rugalmas, sok mindennel kombinálható megoldások), és melyek korlátozzák erősen a többi választást (például az ipari robot zárt cellában).
- A változatossági javaslat a már kiválasztott koncepcióktól legtávolabbi összeférhető kombinációkat keresi. Ez nem értékelés, hanem a megoldástér lefedésének eszköze: a javasolt koncepciót a csapatnak kell megvizsgálnia, értelmes-e.
"""),
]
