"""Eseményfa (eszközlap: Eseményfa)."""
from _kozos import *  # noqa: F401,F403
from openpyxl.formatting.rule import FormulaRule
import itertools

GATAK = [("a BMS leállítja a töltést", 0.99, "gyártói adat a BMS diagnosztikai lefedettségére (becslés)"),
         ("riasztás az üzemeltetőnek", 0.95, "a riasztási lánc próbaüzemi tapasztalata"),
         ("a fémház megfékezi a tüzet", 0.9, "laborvizsgálat (becslés)"),
         ("", None, "")]
LEPCSOS = ["biztonságos leállás", "helyi kár, az üzemeltető beavatkozik", "a dokkolóhely kára", "a tűz átterjed a szomszédos kerékpárokra", ""]
SULY = [1, 2, 3, 5, None]
NG = 4


def keszit():
    wb = uj_munkafuzet()
    utmutato(wb, "Eseményfa – sablon", [
        "■ Mire való? Egy kiinduló eseményből előre követni, hogyan alakul a folyamat attól függően, hogy az egymást követő védelmi rétegek működnek-e, és mekkora az egyes kimenetek gyakorisága (kézikönyv 16. fejezet).",
        "1. A „Bemenet” lapon add meg a kiinduló esemény évi gyakoriságát és legfeljebb négy védelmi réteget a működés (siker) valószínűségével, időrendben.",
        "2. A „Lépcsős fa” lap a gyakori esetet számolja: a következő réteg csak akkor lép működésbe, ha az előző hibázott (például leállítás → riasztás → megfékezés). Minden kimenethez írj leírást és súlyosságot (1–5).",
        "3. A „Teljes fa” lap minden réteget minden ágban megkérdez (2ⁿ sorozat): akkor használd, ha a rétegek egymástól függetlenül, minden esetben működésbe lépnek.",
        "4. A réteg sikervalószínűsége maga is származhat hibafából (hibafa sablon). A szorzatok a rétegek függetlenségét feltételezik.",
        "■ Példa: a VárosiBringa akkumulátorának túlmelegedése töltés közben (kézikönyv 16. fejezet).",
    ])
    be = wb.create_sheet("Bemenet")
    cimsor(be, "Kiinduló esemény és védelmi rétegek")
    szoveg(be["A3"], "Kiinduló esemény:", felkov=True); bemenet(be["C3"], "akkumulátor rendellenes melegedése töltés közben (teljes flotta)")
    szoveg(be["A4"], "Gyakoriság [1/év]:", felkov=True); bemenet(be["C4"], 2)
    tablazat(be, 6, ["Réteg", "Megnevezés", "Siker valószínűsége", "Hiba valószínűsége", "Az adat forrása"], [8, 40, 16, 16, 50],
             [[f"R{i + 1}", g[0] or None, g[1], None, g[2] or None] for i, g in enumerate(GATAK)], bemeneti_oszlopok=(2, 3, 5),
             kepletek={4: lambda r: f'=IF(C{r}="","",1-C{r})'}, formatumok={3: "0.000", 4: "0.000"})
    be.column_dimensions["C"].width = 16
    ls = wb.create_sheet("Lépcsős fa")
    cimsor(ls, "Lépcsős eseményfa: a következő réteg csak az előző hibája esetén lép működésbe")
    fej = ["Sorozat", "Útvonal", "Valószínűség", "Gyakoriság [1/év]", "Kimenet", "Súlyosság (1–5)", "Visszatérési idő [év]"]
    sor = []
    for i in range(NG + 1):
        sor.append([f"S{i + 1}", None, None, None, LEPCSOS[i] or None, SULY[i], None])
    def ut(r, i):
        reszek = [f'IF(Bemenet!$C${7 + j}="","","R{j + 1} hiba, ")' for j in range(i)]
        utolso = f'IF(Bemenet!$C${7 + i}="","","R{i + 1} siker")' if i < NG else '""'
        return "=" + "&".join(reszek + [utolso]) if reszek else "=" + utolso
    def val(r, i):
        hibak = "*".join(f"Bemenet!$D${7 + j}" for j in range(i)) or "1"
        if i < NG:
            return f'=IF(OR(Bemenet!$C${7 + i}="",COUNT(Bemenet!$C$7:$C${7 + i})<{i + 1}),"",{hibak}*Bemenet!$C${7 + i})'
        return f'=IF(COUNT(Bemenet!$C$7:$C$10)<{NG},"",{hibak})'
    kepl = {}
    u = tablazat(ls, 3, fej, [9, 40, 14, 16, 44, 14, 18], sor, bemeneti_oszlopok=(5, 6), formatumok={3: "0.0000E+00", 4: "0.000E+00", 7: "#,##0"})
    n = "COUNT(Bemenet!$C$7:$C$10)"
    for i in range(NG + 1):
        r = 4 + i
        hibak = "*".join(f"Bemenet!$D${7 + j}" for j in range(i)) or "1"
        szoveg_ut = ", ".join([f"R{j + 1} hiba" for j in range(i)] + ([f"R{i + 1} siker"] if i < NG else []))
        if i < NG:
            keplet(ls.cell(row=r, column=2), f'=IF({i}<{n},"{szoveg_ut}",IF({i}={n},"minden réteg hibázik",""))')
            keplet(ls.cell(row=r, column=3), f'=IF({i}<{n},{hibak}*Bemenet!$C${7 + i},IF({i}={n},PRODUCT(Bemenet!$D$7:$D$10),""))', "0.0000E+00")
        else:
            keplet(ls.cell(row=r, column=2), f'=IF({i}={n},"minden réteg hibázik","")')
            keplet(ls.cell(row=r, column=3), f'=IF({i}={n},PRODUCT(Bemenet!$D$7:$D$10),"")', "0.0000E+00")
        keplet(ls.cell(row=r, column=4), f'=IF(C{r}="","",Bemenet!$C$4*C{r})', "0.000E+00")
        keplet(ls.cell(row=r, column=7), f'=IF(OR(D{r}="",D{r}=0),"",1/D{r})', "#,##0.0")
    szoveg(ls.cell(row=u + 2, column=1), "Ellenőrzés: a valószínűségek összege (1 kell legyen):", felkov=True)
    ls.merge_cells(start_row=u + 2, start_column=1, end_row=u + 2, end_column=2)
    keplet(ls.cell(row=u + 2, column=3), f"=SUM(C4:C{u})", "0.000000", True)
    szoveg(ls.cell(row=u + 3, column=1), "Megjegyzés: n megadott rétegnél az S1…Sn sorozat az egyes rétegek sikere, az S(n+1) a „minden réteg hibázik” kimenet; a további sorok üresek.")
    t = wb.create_sheet("Teljes fa")
    cimsor(t, "Teljes eseményfa: minden réteg minden ágban (2⁴ = 16 sorozat)")
    fej = ["Sorozat", "R1", "R2", "R3", "R4", "Valószínűség", "Gyakoriság [1/év]", "Kimenet (írd be)"]
    fejlec(t, 3, fej, [9, 8, 8, 8, 8, 14, 16, 44])
    for n, kombi in enumerate(itertools.product(["S", "H"], repeat=NG)):
        r = 4 + n
        szoveg(t.cell(row=r, column=1), f"T{n + 1}")
        tenyezok = []
        for j, x in enumerate(kombi):
            c = t.cell(row=r, column=2 + j, value=x); c.alignment = kozep; c.font = alap_font
            tenyezok.append(f'IF(Bemenet!$C${7 + j}="",IF(\"{x}\"="S",1,0),{"Bemenet!$C$" if x == "S" else "Bemenet!$D$"}{7 + j})')
        keplet(t.cell(row=r, column=6), "=" + "*".join(tenyezok), "0.0000E+00")
        keplet(t.cell(row=r, column=7), f"=Bemenet!$C$4*F{r}", "0.000E+00")
        bemenet(t.cell(row=r, column=8))
    t.conditional_formatting.add("B4:E19", FormulaRule(formula=['B4="H"'], fill=PatternFill("solid", fgColor="F6DEDE")))
    szoveg(t["A21"], "Ha egy réteg nincs megadva, az ágai közül csak a „siker” sor marad (valószínűség 1, a „hiba” sor 0).")
    keplet(t["F22"], "=SUM(F4:F19)", "0.000000", True); szoveg(t["A22"], "Összeg (1 kell legyen):", felkov=True)
    return mentes(wb, "esemenyfa_sablon.xlsx")
