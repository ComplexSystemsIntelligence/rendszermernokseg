"""A KoboCella konfigurációkezelési példája (sablon és notebook közös adatai).

Konfigurációs elemek (CI), a köztük lévő hatáskapcsolatok és a változáskérelmek.
A kapcsolat iránya: forrás -> cél, azaz a forrás módosítása után a célt ellenőrizni kell.
"""
import datetime as _dt

_D = _dt.date

# az., megnevezés, típus, alapvonal, változat, állapot, felelős, tárolás
CI = [
    ("CI-01", "Rendszerkövetelmény-specifikáció", "dokumentum", "funkcionális", "2.1", "alapvonalban", "rendszermérnök", "PLM/követelmények"),
    ("CI-02", "Rendszerarchitektúra", "dokumentum", "allokált", "1.3", "alapvonalban", "rendszermérnök", "PLM/architektúra"),
    ("CI-03", "ICD I-06: kezelő–kezelőfelület", "dokumentum", "allokált", "1.2", "alapvonalban", "ergonómus", "PLM/interfészek"),
    ("CI-04", "ICD I-07: csavarozó vezérlő–MES", "dokumentum", "allokált", "0.4", "tervezet", "informatikus", "PLM/interfészek"),
    ("CI-05", "Kockázatértékelés és biztonsági igazolás", "dokumentum", "allokált", "1.2", "alapvonalban", "biztonsági mérnök", "PLM/biztonság"),
    ("CI-06", "Cellavezérlő PLC-programja", "szoftver", "termék", "3.5", "alapvonalban", "automatizálási mérnök", "Git/plc"),
    ("CI-07", "Kobotprogram", "szoftver", "termék", "2.7", "módosítás alatt", "robotprogramozó", "Git/kobot"),
    ("CI-08", "Biztonsági PLC programja", "szoftver", "termék", "1.5", "alapvonalban", "biztonsági mérnök", "Git/safety"),
    ("CI-09", "Kezelőfelület-alkalmazás (HMI)", "szoftver", "termék", "2.3", "alapvonalban", "automatizálási mérnök", "Git/hmi"),
    ("CI-10", "Csavarozási paraméterkészlet", "adat", "termék", "1.8", "alapvonalban", "technológus", "Git/csavarozo"),
    ("CI-11", "Befogó készülék gyártási rajzai", "hardver", "termék", "rev. D", "alapvonalban", "gépészmérnök", "PLM/rajzok"),
    ("CI-12", "Villamos kapcsolási rajz", "hardver", "termék", "rev. E", "alapvonalban", "villamosmérnök", "PLM/rajzok"),
    ("CI-13", "Tervezési FMEA", "dokumentum", "termék", "1.5", "alapvonalban", "minőségügyi mérnök", "PLM/kockázat"),
    ("CI-14", "Kezelési útmutató", "dokumentum", "termék", "1.4", "alapvonalban", "ergonómus", "PLM/dokumentáció"),
    ("CI-15", "Feladatelemzés (HTA)", "dokumentum", "allokált", "1.2", "alapvonalban", "ergonómus", "PLM/ember-gép"),
    ("CI-16", "Képzési anyag", "dokumentum", "termék", "1.1", "alapvonalban", "műszakvezető", "PLM/dokumentáció"),
    ("CI-17", "Karbantartási utasítás", "dokumentum", "termék", "1.1", "alapvonalban", "karbantartási vezető", "PLM/dokumentáció"),
    ("CI-18", "Verifikációs mátrix (RVM)", "dokumentum", "termék", "1.7", "alapvonalban", "rendszermérnök", "PLM/verifikáció"),
]

# forrás -> célok
KAPCSOLATOK = {
    "CI-01": ["CI-02", "CI-18"],
    "CI-02": ["CI-03", "CI-04", "CI-05", "CI-12"],
    "CI-03": ["CI-09", "CI-12", "CI-14", "CI-15"],
    "CI-04": ["CI-06", "CI-10", "CI-18"],
    "CI-05": ["CI-08", "CI-14", "CI-16"],
    "CI-06": ["CI-18"],
    "CI-07": ["CI-05", "CI-18"],
    "CI-08": ["CI-05", "CI-18"],
    "CI-09": ["CI-14", "CI-18"],
    "CI-10": ["CI-18"],
    "CI-11": ["CI-07", "CI-13", "CI-17"],
    "CI-12": ["CI-06", "CI-08", "CI-17"],
    "CI-13": ["CI-05", "CI-17"],
    "CI-14": ["CI-16"],
    "CI-15": ["CI-14", "CI-16"],
    "CI-17": ["CI-16"],
}

HATAS_JELLEMZOK = ["Alapvonal, specifikáció", "Költség", "Biztonság", "Interfész", "Képzés", "Leszállított termék"]

# az., cím, fajta, kezdeményező, beadva, hatásjellemzők (6 db igen/nem), döntés, döntés dátuma, lezárva,
# hatáselemzés: {CI: "x" (módosítandó) | "n" (ellenőrizve, nem érinti)}
VK = [
    ("CR-001", "Mértékegység-elírás javítása a követelményspecifikációban (R-07)", "változtatás", "minőségügyi mérnök",
     _D(2026, 1, 12), ["nem"] * 6, "jóváhagyva", _D(2026, 1, 13), _D(2026, 1, 16),
     {"CI-01": "x", "CI-02": "n", "CI-18": "n"}),
    ("CR-002", "Kopásálló betét a befogó ütközőjén", "változtatás", "karbantartási vezető",
     _D(2026, 2, 2), ["nem"] * 6, "jóváhagyva", _D(2026, 2, 5), _D(2026, 2, 27),
     {"CI-11": "x", "CI-13": "x", "CI-17": "x", "CI-07": "n", "CI-16": "n", "CI-05": "n"}),
    ("CR-003", "Második nyugtázó gomb a kezelői oldalon", "változtatás", "validációs csoport",
     _D(2026, 3, 10), ["nem", "nem", "nem", "igen", "igen", "nem"], "jóváhagyva", _D(2026, 3, 17), _D(2026, 4, 14),
     {"CI-03": "x", "CI-09": "x", "CI-12": "x", "CI-06": "x", "CI-14": "x", "CI-15": "x", "CI-16": "x", "CI-18": "x",
      "CI-05": "n", "CI-08": "n", "CI-17": "n"}),
    ("CR-004", "Kobotpálya módosítása a ciklusidő csökkentésére", "változtatás", "technológus",
     _D(2026, 4, 8), ["nem", "nem", "igen", "nem", "nem", "nem"], "jóváhagyva", _D(2026, 4, 15), None,
     {"CI-07": "x"}),
    ("CR-005", "Elírások javítása a kezelési útmutatóban", "változtatás", "műszakvezető",
     _D(2026, 4, 13), ["nem"] * 6, "jóváhagyva", _D(2026, 4, 14), _D(2026, 4, 17),
     {"CI-14": "x", "CI-16": "n"}),
    ("CR-006", "Szériaszám mező a csavarozási adatokban (I-07)", "változtatás", "informatikus",
     _D(2026, 5, 4), ["nem", "nem", "nem", "igen", "nem", "nem"], "függőben", None, None,
     {"CI-04": "x", "CI-10": "x"}),
    ("CR-007", "Üzem MES-kapcsolat nélkül négy hétig, kézi adatrögzítéssel", "eltérési engedély", "projektvezető",
     _D(2026, 4, 22), ["nem"] * 6, "jóváhagyva", _D(2026, 4, 24), None,
     {}),
]

ERTEKELES = _D(2026, 5, 18)
