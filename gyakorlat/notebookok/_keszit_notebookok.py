#!/usr/bin/env python3
"""A Gyakorlati útmutató notebookjainak előállítása és tesztelése.

Futtatás:  python3 gyakorlat/notebookok/_keszit_notebookok.py [--teszt] [név ...]
A --teszt kapcsoló minden notebookot végigfuttat (nbclient), a kimenetet nem menti.
"""
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

MAPPA = Path(__file__).resolve().parent
sys.path.insert(0, str(MAPPA))
from _kozos import keszit  # noqa: E402


def modulok(nevek):
    for f in sorted(MAPPA.glob("_nb_*.py")):
        if nevek and f.stem[4:] not in nevek:
            continue
        spec = importlib.util.spec_from_file_location(f.stem, f)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        yield m


def main():
    nevek = [a for a in sys.argv[1:] if not a.startswith("--")]
    teszt = "--teszt" in sys.argv
    hibak = 0
    for m in modulok(nevek):
        ut = keszit(m.NEV, m.CELLAK, MAPPA / f"{m.NEV}.ipynb")
        if not teszt:
            print("kész:", ut.name)
            continue
        import nbformat
        from nbclient import NotebookClient
        with tempfile.TemporaryDirectory() as tmp:
            for x in (MAPPA.parent / "sablonok").glob("*.xlsx"):
                shutil.copy(x, tmp)
            nb = nbformat.read(str(ut), as_version=4)
            try:
                NotebookClient(nb, timeout=180, kernel_name="python3",
                               resources={"metadata": {"path": tmp}}).execute()
                print("OK  ", ut.name)
            except Exception as e:  # noqa: BLE001
                hibak += 1
                print("HIBA", ut.name, str(e)[-800:])
    # a notebookokból készülő ábrák újragenerálásának kikényszerítése
    (MAPPA.parent / "abrak" / "py" / "nb_abrak.py").touch()
    sys.exit(1 if hibak else 0)


if __name__ == "__main__":
    main()
