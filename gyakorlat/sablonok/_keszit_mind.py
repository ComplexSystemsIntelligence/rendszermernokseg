#!/usr/bin/env python3
"""Az összes Excel-sablon előállítása és újraszámoltatása.

Futtatás:  python3 gyakorlat/sablonok/_keszit_mind.py [--recalc]
A --recalc kapcsoló LibreOffice-szal újraszámolja a képleteket, és jelzi a hibákat.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

MAPPA = Path(__file__).resolve().parent
sys.path.insert(0, str(MAPPA))

RECALC = [p for p in ("/mnt/skills/public/xlsx/scripts/recalc.py",) if os.path.exists(p)]


def futtat(fajl):
    spec = importlib.util.spec_from_file_location(fajl.stem, fajl)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "keszit"):
        return mod.keszit()
    return None


def main():
    subprocess.run([sys.executable, str(MAPPA / "_keszit_sablonok.py")], check=True)
    for f in sorted(MAPPA.glob("_gen_*.py")):
        futtat(f)
        print("kész:", f.stem)
    if "--recalc" in sys.argv and RECALC:
        hibas = 0
        for x in sorted(MAPPA.glob("*.xlsx")):
            out = subprocess.run([sys.executable, RECALC[0], str(x), "60"], capture_output=True, text=True).stdout
            try:
                j = json.loads(out)
            except json.JSONDecodeError:
                print(x.name, "HIBA:", out[:300]); hibas += 1; continue
            st = j.get("status", j.get("error"))
            print(f"{x.name:40s} {st} képletek={j.get('total_formulas')} hibák={j.get('total_errors')}")
            if st != "success":
                hibas += 1
                print(json.dumps(j.get("error_summary"), ensure_ascii=False)[:600])
        sys.exit(1 if hibas else 0)


if __name__ == "__main__":
    main()
