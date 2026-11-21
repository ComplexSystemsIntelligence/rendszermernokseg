#!/usr/bin/env python3
"""Renderelés előtti előkészítés (Quarto pre-render).

- a közös webes betűket a könyv `assets/fonts` mappájába másolja;
- a Pannon Egyetem hivatalos logóit a könyv `assets/logo` mappájába másolja;
- elkészíti a borítóképet (`assets/borito.png`), ha elavult;
- lefordítja az elavult ábrákat (TikZ -> PDF + SVG), ha van LaTeX.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

konyv = Path(os.environ.get("QUARTO_PROJECT_DIR", Path.cwd())).resolve()
gyoker = konyv.parent
cel = konyv / "assets" / "fonts"
cel.mkdir(parents=True, exist_ok=True)
for f in (gyoker / "_shared" / "fonts" / "web").glob("*.woff2"):
    t = cel / f.name
    if not t.exists() or t.stat().st_mtime < f.stat().st_mtime:
        shutil.copy2(f, t)

logo = konyv / "assets" / "logo"
logo.mkdir(parents=True, exist_ok=True)
forras = gyoker / "_shared" / "logo"
for f in list(forras.glob("*.svg")) + list((forras / "png").glob("*.png")):
    t = logo / f.name
    if not t.exists() or t.stat().st_mtime < f.stat().st_mtime:
        shutil.copy2(f, t)

if os.environ.get("ABRAK_KIHAGY"):
    print("prepare: ABRAK_KIHAGY – a verziókövetett ábrákat és borítót használom")
elif shutil.which("lualatex") and shutil.which("pdftocairo"):
    subprocess.run([sys.executable, str(gyoker / "_shared" / "scripts" / "abrak.py"), konyv.name],
                   check=True)
    subprocess.run([sys.executable, str(gyoker / "_shared" / "scripts" / "borito.py"), konyv.name],
                   check=True)
else:
    print("prepare: nincs LaTeX, a meglévő ábrákat használom")
