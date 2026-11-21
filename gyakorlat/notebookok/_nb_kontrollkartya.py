import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "sablonok"))
from _spc_adat import ALLANDOK, FORGACS, FORGACS_I, KOBO, KOBO_I, TURES  # noqa: E402
from _kozos import BETOLTO, code, fejresz, md  # noqa: E402

NEV = "kontrollkartya"
CIM = "Kontrollkártyák: átlag- és terjedelemkártya, egyedi értékes kártya, jelzési szabályok és folyamatképesség"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. az I. szakasz adataiból kiszámolja az átlag- és terjedelemkártya, illetve az egyedi értékes és mozgóterjedelem-kártya határait;
2. a II. szakasz adatain alkalmazza a négy jelzési szabályt (Western Electric-szabályok; Montgomery, 2020; NASA RP-1358, 7.14), és megjelöli a különleges okra utaló pontokat;
3. stabil folyamatra kiszámolja a Cp, Cpk, Pp, Ppk indexeket, és hisztogramon mutatja a folyamatot a tűrésmezőben.

A beépített példák a KoboCella csavarozási nyomatéka és a ForgácsTech napi anyagra várása (kézikönyv 25. fejezet; Shewhart, 1931; Montgomery, 2020).
""", sablon="kontrollkartya_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Kontrollkártya eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött kontrollkartya_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
ALLANDOK = ''' + repr(ALLANDOK) + '''   # n: (d2, A2, D3, D4), Montgomery (2020)
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("kontrollkartya_sablon.xlsx")
    fej = pd.read_excel(fajl, sheet_name="X–R", header=None, nrows=7)
    N_RESZ, K_I, ATH, FTH = int(fej.iloc[2, 1]), int(fej.iloc[3, 1]), float(fej.iloc[4, 1]), float(fej.iloc[5, 1])
    xr = pd.read_excel(fajl, sheet_name="X–R", header=7).iloc[:50, 2:12].apply(pd.to_numeric, errors="coerce")
    X = xr.iloc[:, :N_RESZ].dropna(how="any").to_numpy()   # teljes részcsoportok
    im = pd.read_excel(fajl, sheet_name="Egyedi (I-MR)", header=None, nrows=4)
    I_I = int(im.iloc[2, 1])
    egyedi = pd.read_excel(fajl, sheet_name="Egyedi (I-MR)", header=10).iloc[:100, 1]
    egyedi = pd.to_numeric(egyedi, errors="coerce").dropna().to_numpy()
else:
    X = np.array(''' + repr(KOBO) + ''')
    N_RESZ, K_I, (ATH, FTH) = 5, ''' + str(KOBO_I) + ''', ''' + repr(TURES) + '''
    egyedi = np.array(''' + repr(FORGACS) + ''', float)
    I_I = ''' + str(FORGACS_I) + '''
print(f"X–R: {len(X)} részcsoport, n = {N_RESZ}, I. szakasz: {K_I}; egyedi: {len(egyedi)} érték, I. szakasz: {I_I}")
'''),
    md("""## Jelzési szabályok

A Western Electric-szabályok közül a négy legismertebb (Montgomery, 2020): (1) egy pont a ±3σ határon kívül; (2) három egymást követő pontból kettő ugyanazon az oldalon a 2σ-n túl; (3) öt egymást követő pontból négy ugyanazon az oldalon az 1σ-n túl; (4) nyolc egymást követő pont a középvonal ugyanazon oldalán."""),
    code('''
def jelzesek(x, cl, s):
    z = (np.asarray(x) - cl) / s
    jel = {}
    for i in range(len(z)):
        j = []
        if abs(z[i]) > 3: j.append(1)
        for oldal in (1, -1):
            w3, w5, w8 = z[max(0, i - 2):i + 1] * oldal, z[max(0, i - 4):i + 1] * oldal, z[max(0, i - 7):i + 1] * oldal
            if i >= 2 and z[i] * oldal > 2 and (w3 > 2).sum() >= 2: j.append(2)
            if i >= 4 and z[i] * oldal > 1 and (w5 > 1).sum() >= 4: j.append(3)
            if i >= 7 and (w8 > 0).all(): j.append(4)
        if j: jel[i + 1] = sorted(set(j))
    return jel
'''),
    md("## Átlag- és terjedelemkártya"),
    code('''
d2, A2, D3, D4 = ALLANDOK[N_RESZ]
xb, R = X.mean(axis=1), X.max(axis=1) - X.min(axis=1)
CL, Rb = xb[:K_I].mean(), R[:K_I].mean()
sig = Rb / d2; sx = sig / np.sqrt(N_RESZ)
FEH, AEH = CL + A2 * Rb, CL - A2 * Rb
print(f"Középvonal {CL:.4f}, R̄ {Rb:.4f}, σ̂ {sig:.4f}; FEH {FEH:.4f}, AEH {AEH:.4f}; R-kártya FEH {D4 * Rb:.4f}")
J = jelzesek(xb, CL, sx)
print("Jelzések az átlagkártyán (részcsoport: szabályok):", J if J else "nincs")
print("Terjedelem a határ fölött:", [i + 1 for i, r in enumerate(R) if r > D4 * Rb] or "nincs")
I_jel = [k for k in J if k <= K_I]
print("Az I. szakasz stabil." if not I_jel else f"FIGYELEM: az I. szakaszban is van jelzés ({I_jel}); a határokat a különleges okok kizárása után újra kell számolni.")
'''),
    md("## Egyedi értékes kártya (I-MR)"),
    code('''
MR = np.abs(np.diff(egyedi))
CLi, MRb = egyedi[:I_I].mean(), MR[:I_I - 1].mean()
si = MRb / 1.128
FEHi, AEHi = CLi + 3 * si, max(0.0, CLi - 3 * si)
print(f"Középvonal {CLi:.1f}, MR̄ {MRb:.2f}, σ̂ {si:.2f}; FEH {FEHi:.1f}, AEH {AEHi:.1f}; MR-kártya FEH {3.267 * MRb:.1f}")
Ji = {k: v for k, v in jelzesek(egyedi, CLi, si).items() if 1 in v or 4 in v}
print("Jelzések (1. és 4. szabály):", Ji if Ji else "nincs")
'''),
    md("""## Folyamatképesség

$C_p = (\\mathrm{FTH}-\\mathrm{ATH})/6\\hat{\\sigma}$ és $C_{pk} = \\min(\\mathrm{FTH}-\\mu,\\,\\mu-\\mathrm{ATH})/3\\hat{\\sigma}$ a részcsoporton belüli szórásból; $P_p$ és $P_{pk}$ ugyanez a teljes szórással. Csak stabil folyamatra értelmezhető (Montgomery, 2020)."""),
    code('''
egy = X[:K_I].ravel(); s_teljes = egy.std(ddof=1)
Cp, Cpk = (FTH - ATH) / (6 * sig), min(FTH - CL, CL - ATH) / (3 * sig)
Pp, Ppk = (FTH - ATH) / (6 * s_teljes), min(FTH - CL, CL - ATH) / (3 * s_teljes)
print(f"Cp {Cp:.2f}, Cpk {Cpk:.2f}, Pp {Pp:.2f}, Ppk {Ppk:.2f}")
p_kivul = stats.norm.cdf(ATH, CL, sig) + stats.norm.sf(FTH, CL, sig)
print(f"Normális eloszlást feltételezve a tűrésen kívüli arány ≈ {p_kivul * 1e6:.0f} ppm")
kozep = (ATH + FTH) / 2
print(f"Ha a középérték a tűrésmező közepére ({kozep:g}) kerül: Cpk = {min(FTH - kozep, kozep - ATH) / (3 * sig):.2f}")
'''),
    md("## Ábra"),
    code('''
fig, ax = plt.subplots(1, 3, figsize=(17, 4.8), gridspec_kw={"width_ratios": [1.35, 1.1, 0.9]})
k = np.arange(1, len(xb) + 1)
ax[0].axvspan(K_I + 0.5, len(xb) + 0.5, color="#E6EEF6")
for y, c, ls in [(FEH, "#B83A3A", "-"), (AEH, "#B83A3A", "-"), (CL, "#3E8E63", "-"), (CL + 2 * sx, "#9AA1AB", "--"), (CL - 2 * sx, "#9AA1AB", "--")]:
    ax[0].axhline(y, color=c, ls=ls, lw=1)
ax[0].plot(k, xb, "o-", color="#285780", ms=4)
for i, v in J.items():
    ax[0].plot(i, xb[i - 1], "o", color="#B83A3A" if 1 in v else "#E07B39", ms=8)
    ax[0].annotate(",".join(map(str, v)), (i, xb[i - 1]), xytext=(0, -14), textcoords="offset points", ha="center", fontsize=8, color="#B83A3A")
ax[0].set_xlabel("részcsoport"); ax[0].set_ylabel("átlag"); ax[0].set_title("Átlagkártya (kék sáv: II. szakasz)")
ax[0].spines[["top", "right"]].set_visible(False)

d = np.arange(1, len(egyedi) + 1)
ax[1].axvspan(I_I + 0.5, len(egyedi) + 0.5, color="#E6EEF6")
for y, c in [(FEHi, "#B83A3A"), (CLi, "#3E8E63")]:
    ax[1].axhline(y, color=c, lw=1)
if AEHi > 0: ax[1].axhline(AEHi, color="#B83A3A", lw=1)
ax[1].plot(d, egyedi, "o-", color="#285780", ms=4)
for i in Ji:
    ax[1].plot(i, egyedi[i - 1], "o", color="#B83A3A", ms=8)
ax[1].set_xlabel("sorszám"); ax[1].set_ylabel("érték"); ax[1].set_title("Egyedi értékes kártya")
ax[1].spines[["top", "right"]].set_visible(False)

ax[2].hist(egy, bins=12, density=True, color="#A9C4DE", edgecolor="white")
xs = np.linspace(min(ATH, egy.min()) - 0.02, max(FTH, egy.max()) + 0.02, 300)
ax[2].plot(xs, stats.norm.pdf(xs, CL, sig), color="#285780")
for t in (ATH, FTH):
    ax[2].axvline(t, color="#B83A3A", lw=1.2)
ax[2].set_title(f"Képesség: Cp {Cp:.2f}, Cpk {Cpk:.2f}".replace(".", ",")); ax[2].set_xlabel("érték"); ax[2].set_yticks([])
ax[2].spines[["top", "right", "left"]].set_visible(False)
plt.tight_layout(); plt.savefig("kontrollkartya.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""## Értelmezés

- A KoboCella nyomatéka az I. szakaszban stabil; a 24. részcsoportnál két futási szabály jelez, a 25. pont már a határon kívül van. A futási szabályok az elmozdulást a határátlépés előtt jelezték.
- A Cpk 1,20, mert a középérték 0,02 Nm-rel a tűrésmező közepe fölött van; a középérték beállításával a Cpk a Cp-hez (1,34) közelít.
- A ForgácsTech napi anyagra várásánál a 31. nap a határ fölött van (beszállítói késés): különleges ok, amelyet külön kell kezelni, nem a folyamat átlagos teljesítményének romlása.
"""),
]
