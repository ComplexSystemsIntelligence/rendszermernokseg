"""KoboCella-projekt: WBS, ütemezés (hárompontos becslés) és megszerzett érték (közös adat a WBS-sablonhoz és -notebookhoz)."""

# kód, megnevezés, felelős, költség [MFt] (csak a munkacsomagoknál), elkészültség a 4. hónap végén
WBS = [
    ("1", "Projektirányítás és rendszermérnökség", "projektvezető", None, None),
    ("1.1", "Tervezés és követés", "projektvezető", 2.5, 0.50),
    ("1.2", "Követelmények, konfiguráció", "rendszermérnök", 2.0, 0.60),
    ("1.3", "Kockázat, biztonság", "biztonsági mérnök", 2.5, 0.60),
    ("1.4", "Felülvizsgálatok", "rendszermérnök", 1.0, 0.50),
    ("2", "A cella (termék)", "rendszermérnök", None, None),
    ("2.1", "Vezérlés, biztonsági rendszer", "robotintegrátor", 9.0, 0.60),
    ("2.2", "Kobot, befogó készülék", "robotintegrátor", 18.0, 0.55),
    ("2.3", "Csavarozó egység", "beszállító", 12.0, 0.60),
    ("2.4", "Kezelőfelület", "rendszermérnök", 3.0, 0.50),
    ("2.5", "MES-kapcsolat", "informatika", 4.0, 0.50),
    ("2.6", "Cellakeret, védőrács", "gyártástechnológus", 6.0, 0.70),
    ("3", "Integráció, verifikáció, validáció", "rendszermérnök", None, None),
    ("3.1", "Integráció", "robotintegrátor", 4.5, 0.0),
    ("3.2", "Gyári átvétel (FAT)", "projektvezető", 2.0, 0.0),
    ("3.3", "Helyszíni átvétel (SAT)", "projektvezető", 2.5, 0.0),
    ("3.4", "Validáció kezelőkkel", "ergonómus", 1.0, 0.0),
    ("4", "Telepítés és átadás", "projektvezető", None, None),
    ("4.1", "Helyszín előkészítése", "karbantartás", 2.5, 0.48),
    ("4.2", "Szállítás, telepítés", "robotintegrátor", 2.5, 0.0),
    ("4.3", "Képzés", "ergonómus", 1.5, 0.0),
    ("4.4", "Dokumentáció", "rendszermérnök", 1.5, 0.10),
]

# azonosító, tevékenység, WBS-kód, optimista, legvalószínűbb, pesszimista [hét], előzmények
TEV = [
    ("A1", "Követelmények, alapvonal (SRR)", "1.2", 2, 3, 5, []),
    ("A2", "Részletes terv, felülvizsgálat (CDR)", "1.4", 3, 4, 6, ["A1"]),
    ("A3", "Vezérlés, biztonsági rendszer", "2.1", 6, 8, 11, ["A2"]),
    ("A4", "Kobot, befogó beszerzése", "2.2", 10, 12, 18, ["A2"]),
    ("A5", "Csavarozó egység (beszállító)", "2.3", 8, 9, 13, ["A2"]),
    ("A6", "Kezelőfelület", "2.4", 4, 6, 9, ["A2"]),
    ("A7", "MES-kapcsolat", "2.5", 4, 6, 10, ["A2"]),
    ("A8", "Cellakeret, védőrács", "2.6", 4, 5, 7, ["A2"]),
    ("M1", "Mérföldkő: hardverelemek készen", "–", 0, 0, 0, ["A3", "A4", "A5", "A8"]),
    ("M2", "Mérföldkő: szoftverelemek készen", "–", 0, 0, 0, ["A6", "A7"]),
    ("A9", "Integráció", "3.1", 4, 5, 8, ["M1", "M2"]),
    ("A10", "Gyári átvétel (FAT)", "3.2", 0.5, 1, 2, ["A9"]),
    ("A11", "Helyszín előkészítése", "4.1", 3, 4, 6, ["A2"]),
    ("A12", "Szállítás, telepítés", "4.2", 0.5, 1, 2, ["A10", "A11"]),
    ("A13", "Helyszíni átvétel (SAT)", "3.3", 1, 1, 2, ["A12"]),
    ("A14", "Képzés", "4.3", 1, 2, 3, ["A12"]),
    ("A15", "Validáció kezelőkkel", "3.4", 1, 2, 3, ["A13", "A14"]),
    ("A16", "Dokumentáció, átadás", "4.4", 0.5, 1, 2, ["A15"]),
]

CEL_HET = 35          # a jóváhagyott időtartam (8 hónap) hétben
BAC = 78.0
HONAP = [1, 2, 3, 4, 5, 6, 7, 8]
PV = [4, 10, 22, 41, 58, 68, 74, 78]
EV = [3.5, 9, 19, 36]
AC = [4, 10.5, 21.5, 40]
