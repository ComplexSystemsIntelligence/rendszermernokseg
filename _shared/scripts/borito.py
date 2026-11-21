#!/usr/bin/env python3
"""A könyv borítóképe (assets/borito.png) a PDF-címoldal arculatával.

A címoldalt ugyanazzal a LaTeX-preambulummal szedi, mint a PDF-kötetet,
majd az első oldalt PNG-be alakítja. A kép az EPUB borítója és a webes
kezdőoldal borítóképe. Csak akkor fut le, ha a kép hiányzik vagy elavult.

Használat: python3 _shared/scripts/borito.py kezikonyv [gyakorlat ...]
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

GYOKER = Path(__file__).resolve().parents[2]
SZELESSEG = 1600  # px

SABLON = r"""\documentclass[open=any,headings=standardclasses,chapterprefix=false,paper=a4,fontsize=10.5pt]{scrbook}
\usepackage{fontspec}
\setmainfont{IBM Plex Serif}\setsansfont{IBM Plex Sans}
\usepackage{graphicx}
\usepackage{hyperref}
\input{../_shared/latex/preamble.tex}
\title{%(title)s}
\subtitle{%(subtitle)s}
\author{%(author)s}
\date{%(date)s}
\begin{document}
\maketitle
\end{document}
"""


def elavult(cel: Path, forrasok: list[Path]) -> bool:
    if not cel.exists():
        return True
    t = cel.stat().st_mtime
    return any(f.exists() and f.stat().st_mtime > t for f in forrasok)


def borito(konyv: str) -> None:
    kdir = GYOKER / konyv
    cel = kdir / "assets" / "borito.png"
    forrasok = [kdir / "_quarto.yml", GYOKER / "_shared" / "latex" / "preamble.tex",
                Path(__file__)] + list((GYOKER / "_shared" / "logo" / "pdf").glob("*.pdf"))
    if not elavult(cel, forrasok):
        print(f"borito: {konyv} naprakész")
        return
    book = yaml.safe_load((kdir / "_quarto.yml").read_text(encoding="utf-8"))["book"]
    tex = SABLON % {k: str(book.get(k, "")) for k in ("title", "subtitle", "author", "date")}
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "borito.tex").write_text(tex, encoding="utf-8")
        for _ in range(2):  # remember picture: két futás kell
            subprocess.run(["lualatex", "-interaction=nonstopmode", "-halt-on-error",
                            f"-output-directory={tmp}", str(Path(tmp) / "borito.tex")],
                           cwd=kdir, check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["pdftocairo", "-png", "-singlefile", "-f", "1", "-l", "1",
                        "-scale-to-x", str(SZELESSEG), "-scale-to-y", "-1",
                        str(Path(tmp) / "borito.pdf"), str(Path(tmp) / "borito")], check=True)
        cel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(tmp) / "borito.png", cel)
    print(f"borito: {cel.relative_to(GYOKER)} elkészült")


if __name__ == "__main__":
    for k in sys.argv[1:] or ["kezikonyv", "gyakorlat"]:
        borito(k)
