"""Ábrák előállítása a notebookok beépített példáiból.

A notebookok kódcelláit nem interaktív módban (Agg) lefuttatja egy ideiglenes
mappában, és a megadott PNG-kimeneteket az ábramappába másolja. Így a
Gyakorlati útmutató ábrái pontosan azt mutatják, amit a notebook készít.
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

GEN = Path(sys.argv[1])
NB = Path(__file__).resolve().parents[2] / "notebookok"
SABLON = Path(__file__).resolve().parents[2] / "sablonok"

# notebook -> [(a notebook kimenete, az ábra neve)]
ABRAK = {
    "kontextusdiagram": [("kontextusdiagram.png", "kontextus-varosibringa.png")],
    "erdekelt_felek": [("hatalom_erdekeltseg.png", "nb-hatalom-erdekeltseg.png")],
    "tpm_kovetes": [("tpm_kovetes.png", "nb-tpm-kovetes.png")],
    "nyomonkovetes": [("nyomonkovetes.png", "nb-nyomonkovetes.png")],
    "qfd_minoseghaz": [("qfd_fontossag.png", "nb-qfd-fontossag.png")],
    "funkciofa": [("funkciofa_allokacio.png", "nb-funkciofa-allokacio.png")],
    "n2_dsm": [("dsm_klaszter.png", "nb-dsm-klaszter.png")],
    "morfologiai_doboz": [("morf_gyakorisag.png", "nb-morf-gyakorisag.png")],
    "otletertekeles": [("delphi_konvergencia.png", "nb-delphi.png")],
    "trade_study": [("trade_montecarlo.png", "nb-trade-montecarlo.png")],
    "maut": [("maut_fuggvenyek.png", "nb-maut-fuggvenyek.png")],
    "ahp": [("ahp_prioritas.png", "nb-ahp-prioritas.png")],
    "pareto_front": [("pareto_front.png", "nb-pareto-front.png")],
    "koltseg_haszon": [("kh_montecarlo.png", "nb-kh-montecarlo.png")],
    "hta": [("hta_idodiagram.png", "nb-hta-idodiagram.png")],
    "funkciomegosztas": [("loa_hoterkep.png", "nb-loa-hoterkep.png")],
    "tlx_sus": [("tlx_sus.png", "nb-tlx-sus.png")],
    "kockazati_matrix": [("kockazati_matrix.png", "nb-kockazati-matrix.png")],
    "pha": [("pha_csokkentes.png", "nb-pha-csokkentes.png")],
    "fmea": [("fmea_elemzes.png", "nb-fmea-elemzes.png")],
    "rbd": [("rbd_elemzes.png", "nb-rbd-elemzes.png")],
    "hibafa": [("hibafa_elemzes.png", "nb-hibafa-elemzes.png")],
    "esemenyfa": [("esemenyfa.png", "nb-esemenyfa.png")],
    "stpa": [("stpa.png", "nb-stpa.png")],
    "turesek": [("turesek.png", "nb-turesek.png")],
    "doe": [("doe.png", "nb-doe.png")],
    "folyamatabra_vsm": [("folyamatabra_vsm.png", "nb-folyamatabra-vsm.png")],
    "kapacitas": [("kapacitas.png", "nb-kapacitas.png")],
    "sorkiegyenlites": [("sorkiegyenlites.png", "nb-sorkiegyenlites.png")],
    "oee": [("oee.png", "nb-oee.png")],
    "bpmn": [("bpmn.png", "nb-bpmn.png")],
    "gantt": [("gantt.png", "nb-gantt.png")],
    "abc": [("abc.png", "nb-abc.png")],
    "sorbanallas": [("sorbanallas.png", "nb-sorbanallas.png")],
    "integracios_terv": [("integracios_terv.png", "nb-integracios-terv.png")],
    "rvm": [("rvm.png", "nb-rvm.png")],
    "hasznalhatosagi_teszt": [("hasznalhatosagi_teszt.png", "nb-hasznalhatosagi-teszt.png")],
    "pareto": [("pareto.png", "nb-pareto.png")],
    "halszalka": [("halszalka.png", "nb-halszalka.png")],
    "kontrollkartya": [("kontrollkartya.png", "nb-kontrollkartya.png")],
    "hisztogram_szoras": [("hisztogram_szoras.png", "nb-hisztogram-szoras.png")],
    "folyamatbanyaszat": [("folyamatbanyaszat.png", "nb-folyamatbanyaszat.png")],
    "wbs": [("wbs.png", "nb-wbs.png")],
    "konfiguracio": [("konfiguracio.png", "nb-konfiguracio.png")],
}


def futtat(nev, kimenetek):
    nb = json.loads((NB / f"{nev}.ipynb").read_text(encoding="utf-8"))
    kod = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    elo = (
        "import matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as _plt\n"
        "_eredeti = _plt.savefig\n"
        "def _mentes(f, *a, **k):\n"
        "    _eredeti(f, *a, **k)\n"
        "    if str(f).endswith('.png'):\n"
        "        k.pop('dpi', None)\n"
        "        for kit in ('.svg', '.pdf'):\n"
        "            _eredeti(str(f)[:-4] + kit, *a, **k)\n"
        "_plt.savefig = _mentes\n"
        "import matplotlib.figure as _mf\n"
        "_feredeti = _mf.Figure.savefig\n"
        "def _fmentes(self, f, *a, **k):\n"
        "    _feredeti(self, f, *a, **k)\n"
        "    if str(f).endswith('.png'):\n"
        "        k.pop('dpi', None)\n"
        "        for kit in ('.svg', '.pdf'):\n"
        "            _feredeti(self, str(f)[:-4] + kit, *a, **k)\n"
        "_mf.Figure.savefig = _fmentes\n"
    )
    kod = elo + kod
    kod = kod.replace("plt.show()", "plt.close('all')").replace("display(", "(lambda *a, **k: None)(")
    regi = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        for x in SABLON.glob("*.xlsx"):
            shutil.copy(x, tmp)
        os.chdir(tmp)
        try:
            exec(compile(kod, nev, "exec"), {"__name__": "__main__", "display": lambda *a, **k: None})
        finally:
            os.chdir(regi)
        for forras, cel in kimenetek:
            for kit in (".png", ".svg", ".pdf"):
                f = Path(tmp) / (forras[:-4] + kit)
                if f.exists():
                    shutil.copy(f, GEN / (cel[:-4] + kit))


SZURO = set(sys.argv[2:])
for nev, kimenetek in ABRAK.items():
    if SZURO and nev not in SZURO:
        continue
    futtat(nev, kimenetek)
