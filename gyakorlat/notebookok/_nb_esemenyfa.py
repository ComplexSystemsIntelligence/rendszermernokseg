from _kozos import BETOLTO, code, fejresz, md

NEV = "esemenyfa"
CIM = "Eseményfa: kimenetek gyakorisága, a fa kirajzolása, érzékenység a védelmi rétegekre"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. a kiinduló esemény gyakoriságából és a védelmi rétegek sikervalószínűségéből kiszámítja a kimenetek gyakoriságát (lépcsős fa: a következő réteg csak az előző hibája esetén lép működésbe);
2. kirajzolja az eseményfát;
3. megvizsgálja, hogyan változik a legsúlyosabb kimenet gyakorisága, ha egy réteg hibavalószínűsége tízszeresére nő vagy tizedére csökken.

A beépített példa a VárosiBringa akkumulátorának túlmelegedése (kézikönyv 16. fejezet).
""", sablon="esemenyfa_sablon.xlsx", eszkozlap="Gyakorlati útmutató, Eseményfa eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött esemenyfa_sablon.xlsx
''' + BETOLTO + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("esemenyfa_sablon.xlsx")
    b = pd.read_excel(fajl, sheet_name="Bemenet", header=None)
    kiindulo, f0 = str(b.iloc[2, 2]), float(b.iloc[3, 2])
    r = b.iloc[6:10, 1:3]; r = r[r.iloc[:, 1].notna()]
    retegek = list(r.iloc[:, 0].astype(str)); siker = r.iloc[:, 1].astype(float).to_numpy()
    l = pd.read_excel(fajl, sheet_name="Lépcsős fa", header=2).iloc[:len(retegek) + 1]
    kimenetek = list(l.iloc[:, 4].fillna("").astype(str)); sulyossag = list(l.iloc[:, 5])
else:
    kiindulo, f0 = "akkumulátor melegedése töltés közben", 2.0
    retegek = ["a BMS leállítja a töltést", "riasztás az üzemeltetőnek", "a fémház megfékezi a tüzet"]
    siker = np.array([0.99, 0.95, 0.9])
    kimenetek = ["biztonságos leállás", "helyi kár, beavatkozás", "a dokkolóhely kára", "a tűz átterjed"]
    sulyossag = [1, 2, 3, 5]

def kimenet_gyakorisag(siker):
    hiba = 1 - siker
    v = [np.prod(hiba[:i]) * siker[i] for i in range(len(siker))] + [np.prod(hiba)]
    return f0 * np.array(v)

gy = kimenet_gyakorisag(siker)
tabla = pd.DataFrame({"kimenet": kimenetek, "súlyosság": sulyossag, "gyakoriság [1/év]": gy, "visszatérési idő [év]": 1 / gy})
print(f"Ellenőrzés: Σ gyakoriság = {gy.sum():.4f} (a kiinduló esemény: {f0})")
tabla
'''),
    md("## Érzékenység"),
    code('''
legsulyosabb = int(np.argmax(sulyossag))
alap = gy[legsulyosabb]
erz = []
for i, nev in enumerate(retegek):
    sor = {}
    for jel, szorzo in (("rosszabb (hiba × 10)", 10), ("jobb (hiba / 10)", 0.1)):
        s = siker.copy(); s[i] = 1 - min(1, (1 - s[i]) * szorzo)
        sor[jel] = kimenet_gyakorisag(s)[legsulyosabb] / alap
    erz.append({"réteg": nev, **sor})
erz = pd.DataFrame(erz)
print(f"A legsúlyosabb kimenet ({kimenetek[legsulyosabb]}) alapgyakorisága: {alap:.2e}/év")
erz
'''),
    md("## Ábra"),
    code('''
n = len(retegek)
fig, axs = plt.subplots(1, 2, figsize=(15, 4.8), gridspec_kw={"width_ratios": [1.6, 1]})
ax = axs[0]
import textwrap
x0, dx = 0.0, 2.2
ax.text(x0 - 0.1, 0, f"{kiindulo}\\n({f0:g}/év)", ha="right", va="center", fontsize=8,
        bbox=dict(boxstyle="round", fc="#FBE7D9", ec="#E07B39"))
y = 0.0
SZ = {1: "#DDEFE4", 2: "#E6EEF6", 3: "#FBE7D9", 4: "#F6DEDE", 5: "#F6DEDE"}
for i in range(n):
    x = x0 + i * dx
    ax.text(x + dx / 2, 1.25, textwrap.fill(retegek[i], 18), ha="center", va="bottom", fontsize=7.5)
    ys, yh = y + 0.9 / (i + 1), y - 0.9 / (i + 1)
    ax.plot([x, x, x + dx * (n - i)], [y, ys, ys], color="#285780", lw=1.3)
    ax.text(x + 0.05, ys + 0.04, f"siker {siker[i]:g}", fontsize=7)
    ax.plot([x, x, x + dx], [y, yh, yh], color="#B83A3A", lw=1.3)
    ax.text(x + 0.05, yh - 0.1, f"hiba {1 - siker[i]:.2g}", fontsize=7, color="#B83A3A")
    xe = x0 + n * dx
    ax.text(xe + 0.1, ys, f"{kimenetek[i]}: {gy[i]:.2e}/év", va="center", fontsize=8,
            bbox=dict(boxstyle="round", fc=SZ.get(int(sulyossag[i]), "#EEEEEE"), ec="#999999"))
    y = yh
ax.plot([x0 + (n - 1) * dx + dx, x0 + n * dx], [y, y], color="#B83A3A", lw=1.3)
ax.text(x0 + n * dx + 0.1, y, f"{kimenetek[n]}: {gy[n]:.2e}/év", va="center", fontsize=8,
        bbox=dict(boxstyle="round", fc=SZ.get(int(sulyossag[n]), "#EEEEEE"), ec="#B83A3A"))
ax.set_xlim(-3.0, x0 + n * dx + 3.6); ax.set_ylim(y - 0.5, 1.9); ax.axis("off")
ax.set_title("Lépcsős eseményfa", fontsize=10)
ax = axs[1]
yy = np.arange(len(erz))
ax.barh(yy, np.log10(erz["rosszabb (hiba × 10)"]), color="#B83A3A", label="hiba × 10")
ax.barh(yy, np.log10(erz["jobb (hiba / 10)"]), color="#3E8E63", label="hiba / 10")
ax.axvline(0, color="black", lw=0.8)
ax.set_yticks(yy); ax.set_yticklabels(erz["réteg"], fontsize=8); ax.invert_yaxis()
ax.set_xlabel("log10(új / alap gyakoriság) a legsúlyosabb kimenetre"); ax.legend(fontsize=8)
ax.set_title("Érzékenység a rétegek hibavalószínűségére", fontsize=10)
plt.tight_layout(); plt.savefig("esemenyfa.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A kiinduló esemény évi két előfordulásából 1,98 biztonságos leállással végződik; a tűz átterjedése $10^{-4}$/év, vagyis átlagosan tízezer évente egyszer várható a teljes flottára.
- Lépcsős fában minden réteg hibavalószínűsége ugyanúgy, szorzóként hat a legsúlyosabb kimenetre: egy réteg tízszeres romlása tízszeres gyakoriságot jelent. A rétegek közötti választást ezért nem az érzékenység, hanem a javítás költsége és a rétegek függetlensége dönti el.
- A szorzás a rétegek függetlenségét feltételezi. Ha például a BMS és a riasztás ugyanazon a hőmérséklet-érzékelőn alapul, a két réteg hibája nem független, és a valódi gyakoriság nagyobb; ezt a rétegek hibafájával kell vizsgálni.
"""),
]
