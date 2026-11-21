"""Segédfüggvények a Colab-kompatibilis notebookok előállításához.

Minden notebook egy _nb_<név>.py modulban van leírva (NEV, CIM, CELLAK).
A notebookok telepítés nélkül futnak Google Colabban és helyi Jupyterben is:
alapértelmezésben a beépített példaadatokkal dolgoznak, de a kitöltött
Excel-sablon is feltölthető.
"""
import base64
from pathlib import Path

import nbformat as nbf

COLAB = "https://colab.research.google.com/github/ComplexSystemsIntelligence/rendszermernokseg/blob/main/gyakorlat/notebookok/"
SABLON_URL = "https://complexsystemsintelligence.github.io/rendszermernokseg/gyakorlat/sablonok/"
_LOGO = Path(__file__).resolve().parents[2] / "_shared" / "logo" / "png" / "PE_cimer_nevjel_fekvo_kek-96.png"
# A Pannon Egyetem fekvő címer- és névjele beágyazva: Colabban, Jupyterben és a GitHubon is megjelenik
PE_LOGO = ('<img src="data:image/png;base64,' + base64.b64encode(_LOGO.read_bytes()).decode("ascii")
           + '" alt="Pannon Egyetem" height="48">')


def md(s):
    return nbf.v4.new_markdown_cell(s.strip("\n"))


def code(s):
    return nbf.v4.new_code_cell(s.strip("\n"))


def fejresz(nev, cim, leiras, sablon=None, eszkozlap=None):
    sorok = [PE_LOGO, "", f"# {cim}", "", leiras.strip(), ""]
    sorok.append(f"[Megnyitás Google Colabban]({COLAB}{nev}.ipynb) · "
                 "Rendszermérnöki eszköztár – Gyakorlati útmutató · Abonyi János · CC BY-NC-SA 4.0 (szöveg), MIT (kód)")
    sorok += ["", "**Használat.** Futtasd a cellákat sorban (Colabban: *Futtatókörnyezet → Összes futtatása*). "
              "A notebook alapértelmezésben a beépített példaadatokkal dolgozik."]
    if sablon:
        sorok += [f"Saját adataidhoz töltsd ki a [`{sablon}`]({SABLON_URL}{sablon}) sablont, "
                  "állítsd a `SAJAT_SABLON` változót `True` értékre, és futtatáskor töltsd fel a fájlt."]
    if eszkozlap:
        sorok += ["", f"A módszer leírása és értelmezése: {eszkozlap}."]
    return md("\n".join(sorok))


BETOLTO = '''
import sys, os
COLABBAN = "google.colab" in sys.modules

def sablon_betoltese(alapnev):
    """Visszaadja a feltöltött vagy a notebook mellett lévő sablon útvonalát."""
    if COLABBAN:
        from google.colab import files
        print("Válaszd ki a kitöltött sablont:")
        feltoltott = files.upload()
        return next(iter(feltoltott))
    for jelolt in (alapnev, os.path.join("..", "sablonok", alapnev)):
        if os.path.exists(jelolt):
            return jelolt
    raise FileNotFoundError(f"Nem találom: {alapnev}")
'''


def keszit(nev, cellak, utvonal):
    nb = nbf.v4.new_notebook()
    nb.cells = cellak
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "colab": {"provenance": [], "toc_visible": True},
    }
    nbf.write(nb, str(utvonal))
    return utvonal
