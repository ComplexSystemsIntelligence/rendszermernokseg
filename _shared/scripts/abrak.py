#!/usr/bin/env python3
"""Ábrák fordítása a Rendszermérnökség könyvekhez.

Minden könyv `abrak/tikz/*.tex` fájlját lualatex-hel PDF-be fordítja, majd
pdftocairo-val SVG-t készít belőle. Az `abrak/py/*.py` szkriptek (matplotlib)
közvetlenül írnak SVG-t és PDF-et. Az eredmény az `abrak/gen/` mappába kerül.
A PDF-kimenet a LaTeX-könyvbe, az SVG a webes és EPUB-változatba kerül,
így minden formátumban vektorgrafika jelenik meg.

Használat:
    python3 _shared/scripts/abrak.py [kezikonyv|gyakorlat ...] [--force]
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GYOKER = Path(__file__).resolve().parents[2]
TIKZ_STILUS = GYOKER / "_shared" / "tikz"
BETUK = GYOKER / "_shared" / "fonts" / "ttf"


def elavult(forras: Path, *celok: Path) -> bool:
    if any(not c.exists() for c in celok):
        return True
    fm = forras.stat().st_mtime
    stilus_m = max(p.stat().st_mtime for p in TIKZ_STILUS.glob("*"))
    return any(c.stat().st_mtime < max(fm, stilus_m) for c in celok)


def tikz_fordit(tex: Path, gen: Path, force: bool) -> None:
    pdf_cel = gen / (tex.stem + ".pdf")
    svg_cel = gen / (tex.stem + ".svg")
    if not force and not elavult(tex, pdf_cel, svg_cel):
        return
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ)
        env["TEXINPUTS"] = f"{TIKZ_STILUS}{os.pathsep}{tex.parent}{os.pathsep}" + env.get("TEXINPUTS", "")
        parancs = [
            "lualatex", "-interaction=nonstopmode", "-halt-on-error",
            f"-output-directory={tmp}", f"-jobname={tex.stem}",
            rf"\def\peFontPath{{{BETUK.as_posix()}/}}\input{{{tex.as_posix()}}}",
        ]
        r = subprocess.run(parancs, cwd=tex.parent, env=env,
                           capture_output=True, text=True)
        kesz = Path(tmp) / (tex.stem + ".pdf")
        if r.returncode != 0 or not kesz.exists():
            naplo = Path(tmp) / (tex.stem + ".log")
            szoveg = naplo.read_text(errors="replace") if naplo.exists() else r.stdout
            hibak = [s for s in szoveg.splitlines() if s.startswith("!") or "Error" in s]
            print(f"  HIBA: {tex.name}\n    " + "\n    ".join(hibak[:8]), file=sys.stderr)
            raise SystemExit(1)
        shutil.copy(kesz, pdf_cel)
    subprocess.run(["pdftocairo", "-svg", str(pdf_cel), str(svg_cel)], check=True)
    print(f"  kész: {tex.stem} (pdf+svg)")


def py_futtat(szkript: Path, gen: Path, force: bool) -> None:
    jel = gen / (szkript.stem + ".stamp")
    if not force and jel.exists() and jel.stat().st_mtime >= szkript.stat().st_mtime:
        return
    env = dict(os.environ, PE_GEN=str(gen), PE_FONTS=str(BETUK))
    subprocess.run([sys.executable, "-I", str(szkript), str(gen)], check=True, env=env)
    jel.touch()
    print(f"  kész: {szkript.stem} (python)")


def konyv(nev: str, force: bool) -> None:
    alap = GYOKER / nev / "abrak"
    gen = alap / "gen"
    gen.mkdir(parents=True, exist_ok=True)
    print(f"[{nev}] ábrák")
    for tex in sorted((alap / "tikz").glob("*.tex")):
        tikz_fordit(tex, gen, force)
    for py in sorted((alap / "py").glob("*.py")):
        py_futtat(py, gen, force)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    for k in (args or ["kezikonyv", "gyakorlat"]):
        konyv(k, force)
