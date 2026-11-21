#!/usr/bin/env python3
"""Renderelés utáni magyar tipográfiai javítások (Quarto post-render).

A Quarto angol mintájú feliratsorrendjét ("ábra 2.1:") a magyar szokásra
("2.1. ábra.") cseréli, és a fejezet- és szakaszszámok után kiteszi a pontot.
HTML-fájlokon és az EPUB-csomagon belül is elvégzi a cserét.
"""
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

FELIRAT = re.compile(r"(ábra|táblázat|kódrészlet)(?:&nbsp;| | )(\d+(?:\.\d+)*)(?::|\.)\s*")
FEJEZET = re.compile(r'(<span class="chapter-number">)(\d+|[A-Z])(</span>)')
SZAKASZ = re.compile(r'(<span class="header-section-number">)([\dA-Z]+(?:\.\d+)*)(</span>)')


def javit(html: str) -> str:
    def felirat(m):
        return f'<span class="abraszam">{m.group(2)}. {m.group(1)}.</span> '
    # csak a feliratokon belül cserélünk
    html = re.sub(r"(<figcaption[^>]*>)(.*?)(</figcaption>)",
                  lambda m: m.group(1) + FELIRAT.sub(felirat, m.group(2), count=1) + m.group(3),
                  html, flags=re.S)
    html = re.sub(r'(<caption[^>]*>)(.*?)(</caption>)',
                  lambda m: m.group(1) + FELIRAT.sub(felirat, m.group(2), count=1) + m.group(3),
                  html, flags=re.S)
    html = FEJEZET.sub(lambda m: f"{m.group(1)}{m.group(2)}.{m.group(3)}", html)
    html = SZAKASZ.sub(lambda m: f"{m.group(1)}{m.group(2)}.{m.group(3)}", html)
    return html


def epub_javit(utvonal: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(utvonal) as z:
            z.extractall(tmp)
            nevek = z.namelist()
        for n in nevek:
            if n.endswith((".xhtml", ".html")):
                p = Path(tmp) / n
                p.write_text(javit(p.read_text(encoding="utf-8")), encoding="utf-8")
        uj = utvonal.with_suffix(".tmp.epub")
        with zipfile.ZipFile(uj, "w") as z:
            z.write(Path(tmp) / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
            for n in nevek:
                if n != "mimetype" and not n.endswith("/"):
                    z.write(Path(tmp) / n, n, compress_type=zipfile.ZIP_DEFLATED)
        shutil.move(uj, utvonal)


kimenet = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_book"))
if not kimenet.is_absolute():
    kimenet = Path(os.environ.get("QUARTO_PROJECT_DIR", ".")) / kimenet
for f in kimenet.rglob("*.html"):
    s = f.read_text(encoding="utf-8")
    j = javit(s)
    if j != s:
        f.write_text(j, encoding="utf-8")
for e in kimenet.rglob("*.epub"):
    epub_javit(e)
