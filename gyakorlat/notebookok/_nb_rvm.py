from _kozos import BETOLTO, code, fejresz, md

NEV = "rvm"
CIM = "Követelmény-verifikációs mátrix: állapotkövetés, konfidenciahatár, mintaelemszám és sikeres futás próba"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. betölti a követelmény-verifikációs mátrixot és az eltérésnaplót, ellenőrzi a sorokat, és összesíti a verifikáció állapotát módonként;
2. egyoldali konfidenciahatárral eldönti, teljesül-e egy felső vagy alsó korlátos követelmény (Student-féle *t*-eloszlás);
3. a nem centrális *t*-eloszlással kiszámolja a próba erejét és a szükséges mintaelemszámot;
4. sikeres futás próbával, illetve hibás próbák esetén binomiális számítással (Clopper–Pearson-határ) megadja, hány próba igazol egy megbízhatósági követelményt.

A beépített példa a KoboCella verifikációja (kézikönyv 23. fejezet; ISO/IEC/IEEE 15288:2023, 6.4.9.; ECSS-E-ST-10-02C Rev.1, 2018; Montgomery, 2020; O'Connor és Kleyner, 2012; NASA SE Handbook, 5.3. szakasz és D függelék).
""", sablon="rvm_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Követelmény-verifikációs mátrix eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött rvm_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
'''),
    md("## Adatok"),
    code('''
OSZL = ["id", "forras", "kovetelmeny", "kriterium", "mod", "szint", "helyszin", "atvetel", "vegrehajto", "eljaras", "eredmeny", "allapot", "elteres"]
if SAJAT_SABLON:
    fajl = sablon_betoltese("rvm_sablon.xlsx")
    rvm = pd.read_excel(fajl, sheet_name="Mátrix", header=3).iloc[:40, :13]
    rvm.columns = OSZL
    rvm = rvm[rvm.id.notna()].reset_index(drop=True)
    elt = pd.read_excel(fajl, sheet_name="Eltérések", header=3).iloc[:20, :8]
    elt.columns = ["id", "kovetelmeny", "fazis", "leiras", "ok", "intezkedes", "ismetles", "allapot"]
    elt = elt[elt.id.notna()].reset_index(drop=True)
    meres = pd.read_excel(fajl, sheet_name="Statisztika", header=3, usecols="D").iloc[:50, 0]
    meres = pd.to_numeric(meres, errors="coerce").dropna().to_numpy()
    stat = pd.read_excel(fajl, sheet_name="Statisztika", header=None, usecols="A:B", nrows=30)
    TIPUS, HATAR, KONF = stat.iloc[4, 1], float(stat.iloc[5, 1]), float(stat.iloc[6, 1])
else:
    rvm = pd.DataFrame([
        ("R-01", "elemzés és teszt", "rendszer", "SAT (előtte FAT)", "igen", "teljesült", "E-01"),
        ("R-02", "elemzés", "rendszer", "tervezés", "nem", "teljesült", None),
        ("R-03", "teszt", "alrendszer", "FAT és SAT", "igen", "teljesült", "E-03"),
        ("R-05", "elemzés és bemutatás", "rendszer", "FAT", "nem", "teljesült", None),
        ("R-07", "teszt", "rendszer", "FAT", "igen", "teljesült", None),
        ("R-09", "bemutatás", "rendszer", "FAT", "igen", "teljesült", "E-02"),
        ("R-11", "teszt", "rendszer", "FAT", "igen", "teljesült", None),
        ("R-12", "bemutatás", "rendszer", "SAT", "nem", "folyamatban", None),
        ("R-15", "vizsgálat", "rendszer", "telepítés", "nem", "teljesült", None)],
        columns=["id", "mod", "szint", "helyszin", "atvetel", "allapot", "elteres"])
    elt = pd.DataFrame([("E-01", "R-01", "termékhiba", "lezárt"), ("E-02", "R-09", "termékhiba", "lezárt"),
                        ("E-03", "R-03", "mérőeszköz", "lezárt")], columns=["id", "kovetelmeny", "ok", "allapot"])
    meres = np.array([73.8, 74.0, 74.5])     # az R-01 próbaüzem műszakátlagai [s]
    TIPUS, HATAR, KONF = "felső korlát", 75.0, 0.95
print(f"{len(rvm)} követelmény, {len(elt)} eltérésjelentés")
'''),
    md("## A verifikáció állapota"),
    code('''
ALLAPOTOK = ["tervezett", "folyamatban", "teljesült", "nem teljesült", "eltérési engedély"]
tabla = pd.crosstab(rvm["mod"], rvm["allapot"]).reindex(columns=ALLAPOTOK, fill_value=0)
tabla["összesen"] = tabla.sum(axis=1)
print(tabla.to_string())
lezart = rvm.allapot.isin(["teljesült", "eltérési engedély"])
nyitott_elt = (elt.allapot == "nyitott").sum()
print(f"\\nLezárt: {lezart.sum()}/{len(rvm)} ({lezart.mean():.0%}); nyitott eltérés: {nyitott_elt}")
for _, s in rvm.iterrows():
    if s.allapot == "nem teljesült" and pd.isna(s.elteres):
        print(f"FIGYELEM: {s.id} nem teljesült, de nincs eltérésjelentés")
for _, s in rvm[~lezart].iterrows():
    print(f"Nyitott: {s.id} ({s['mod']}, {s.helyszin}): {s.allapot}")
print("A verifikáció lezárható." if lezart.all() and nyitott_elt == 0 else "A verifikáció még nem zárható le.")
print("\\nAz eltérések oka:"); print(elt.ok.value_counts().to_string())
'''),
    md("""## Konfidenciahatár

Felső korlátos követelménynél ($\\mu \\le U$) a döntési szabály: $\\bar{x} + t_{1-\\alpha,n-1}\\, s/\\sqrt{n} \\le U$. A méréseknek függetleneknek kell lenniük; egymást követő ciklusok helyett ezért például műszakátlagokat használunk."""),
    code('''
def konfidenciahatar(x, konf=0.95, felso=True):
    n = len(x); m = np.mean(x); s = np.std(x, ddof=1)
    t = stats.t.ppf(konf, n - 1)
    return m, s, (m + t * s / np.sqrt(n)) if felso else (m - t * s / np.sqrt(n))

felso = TIPUS == "felső korlát"
m, s, hatar = konfidenciahatar(meres, KONF, felso)
teljesul = hatar <= HATAR if felso else hatar >= HATAR
print(f"n = {len(meres)}, átlag = {m:.2f}, s = {s:.3f}, {KONF:.0%}-os {'felső' if felso else 'alsó'} határ = {hatar:.2f} "
      f"→ {'teljesül' if teljesul else 'nem igazolt'} (határérték {HATAR:g})")
'''),
    md("""## A próba ereje és a szükséges mintaelemszám

A próba ereje annak valószínűsége, hogy a követelményt teljesítő terméket a próba valóban megfelelőnek nyilvánítja. A pontos értéket a nem centrális *t*-eloszlás adja; a normális közelítés kis mintánál alulbecsüli a szükséges elemszámot."""),
    code('''
def ero(n, delta, s, konf=0.95):
    df = n - 1; tk = stats.t.ppf(konf, df); ncp = delta / s * np.sqrt(n)
    return 1 - stats.nct.cdf(tk, df, ncp)

delta = abs(HATAR - m)
nn = np.arange(2, 13)
erok = [ero(n, delta, s, KONF) for n in nn]
for n, e in zip(nn, erok):
    print(f"n = {n:2d}: erő = {e:.3f}")
BETA = 0.10
szukseges = next((int(n) for n, e in zip(nn, erok) if e >= 1 - BETA), None)
kozelito = int(np.ceil(((stats.norm.ppf(KONF) + stats.norm.ppf(1 - BETA)) * s / delta) ** 2))
print(f"\\nA {1 - BETA:.0%}-os erőhöz szükséges n: {szukseges} (normális közelítéssel {kozelito}); a mért n = {len(meres)} ereje {ero(len(meres), delta, s, KONF):.0%}.")
'''),
    md("""## Sikeres futás próba és binomiális számítás

$n$ hibátlan, független próba $C$ konfidenciaszinten $R \\ge (1-C)^{1/n}$ megbízhatóságot igazol. Ha $f$ próba hibás, a megbízhatóság alsó határa a Clopper–Pearson-féle egzakt binomiális határ: $R_L = B^{-1}(1-C;\\, n-f,\\, f+1)$, ahol $B^{-1}$ a béta-eloszlás kvantilisfüggvénye."""),
    code('''
def also_hatar(n, f, C):
    return stats.beta.ppf(1 - C, n - f, f + 1)

def szukseges_proba(R, C, f=0):
    n = f + 1
    while stats.binom.cdf(f, n, 1 - R) > 1 - C:
        n += 1
    return n

R_CEL, C_CEL, N_OBS, F_OBS = 0.999, 0.90, 8096, 0
for f in (0, 1, 2):
    print(f"R = {R_CEL}, C = {C_CEL:.0%}, {f} hiba megengedve: {szukseges_proba(R_CEL, C_CEL, f)} próba")
print(f"\\n{N_OBS} próba, {F_OBS} hiba → igazolt megbízhatóság (C = {C_CEL:.0%}): {also_hatar(N_OBS, F_OBS, C_CEL):.5f}")
'''),
    md("## Ábra"),
    code('''
fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
szinek = {"tervezett": "#C9D6E3", "folyamatban": "#E07B39", "teljesült": "#3E8E63", "nem teljesült": "#B83A3A", "eltérési engedély": "#7A5C99"}
bal = np.zeros(len(tabla))
for a in ALLAPOTOK:
    if tabla[a].sum():
        ax[0].barh(tabla.index, tabla[a], left=bal, color=szinek[a], label=a); bal += tabla[a].to_numpy()
ax[0].set_xlabel("követelmény"); ax[0].set_title("Állapot módonként"); ax[0].legend(fontsize=8, frameon=False)
ax[0].invert_yaxis(); ax[0].spines[["top", "right"]].set_visible(False)

ax[1].plot(nn, erok, "o-", color="#285780")
ax[1].axhline(1 - BETA, color="#B83A3A", ls="--", lw=1); ax[1].text(nn[-1], 1 - BETA - 0.05, f"{1 - BETA:.0%}", ha="right", color="#B83A3A", fontsize=9)
ax[1].axvline(len(meres), color="#6B7280", ls=":", lw=1); ax[1].text(len(meres) + 0.15, 0.1, "mért n", color="#6B7280", fontsize=9)
ax[1].set_xlabel("független mérések száma (n)"); ax[1].set_ylabel("a próba ereje"); ax[1].set_ylim(0, 1.03)
ax[1].set_title(f"Konfidenciahatár: átlag {m:.1f}, határ {HATAR:g}".replace(".", ",")); ax[1].grid(alpha=0.3); ax[1].spines[["top", "right"]].set_visible(False)

RR = np.linspace(0.95, 0.9995, 200)
for f, sty in zip((0, 1, 2), ("-", "--", ":")):
    ax[2].plot(RR, [szukseges_proba(r, C_CEL, f) for r in RR], sty, color="#285780", label=f"{f} hiba")
ax[2].scatter([R_CEL], [szukseges_proba(R_CEL, C_CEL, 0)], color="#E07B39", zorder=3)
ax[2].annotate(f"{szukseges_proba(R_CEL, C_CEL, 0)} próba", (R_CEL, szukseges_proba(R_CEL, C_CEL, 0)), xytext=(-95, 8), textcoords="offset points", fontsize=9)
ax[2].set_yscale("log"); ax[2].set_xlabel("igazolandó megbízhatóság (R)"); ax[2].set_ylabel("szükséges próbák száma")
ax[2].set_title(f"Sikeres futás próba (C = {C_CEL:.0%})"); ax[2].legend(fontsize=8, frameon=False); ax[2].grid(alpha=0.3, which="both")
ax[2].spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig("rvm.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""## Értelmezés

- A mátrix akkor zárható le, ha minden követelmény teljesült vagy eltérési engedélyt kapott, és nincs nyitott eltérés. A KoboCella példájában a típusváltás bemutatása (R-12) még folyamatban van.
- A három műszakátlaggal végzett próba ereje kb. 85%; 90%-os erőhöz négy független műszak kellett volna. A próba sikeres volt, de a mintaelemszámot a teszt előtt, az erő alapján érdemes megválasztani.
- Ha a sikeres futás próbában egyetlen hiba is előfordul, a szükséges próbaszám jelentősen nő; a nagy megbízhatóságú követelményeket ezért elemzéssel és alacsonyabb szintű tesztekkel együtt szokás verifikálni.
"""),
]
