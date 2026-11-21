#!/usr/bin/env python3
"""A VárosiBringa minőségházának TikZ-ábrája a közös adatfájlból (_shared/adat/qfd_bringa.json).

Futtatás: python3 kezikonyv/abrak/_qfd_abra.py  →  tikz/qfd-bringa.tex
"""
import json
from pathlib import Path

GY = Path(__file__).resolve().parents[2]
d = json.loads((GY / "_shared" / "adat" / "qfd_bringa.json").read_text(encoding="utf-8"))
E, M, R = d["elvarasok"], d["jellemzok"], d["kapcsolat"]
n, m = len(E), len(M)
w = [e["fontossag"] for e in E]
imp = [sum(w[i] * R[i][j] for i in range(n)) for j in range(m)]
tot = sum(imp)
cw, rh = 0.95, 0.72          # oszlopszélesség, sormagasság (cm)
x0 = 0.0                     # a mátrix bal széle
top = 0.0                    # a mátrix teteje
hh = 4.2                     # a fejléc (jellemzőnevek) magassága

o = [r"\documentclass[tikz,border=6pt]{standalone}", r"\usepackage{peabra}", r"\begin{document}",
     r"\begin{tikzpicture}[x=1cm,y=1cm]"]
X = lambda j: x0 + (j + 0.5) * cw
Y = lambda i: top - (i + 0.5) * rh
# mátrix rács
o.append(rf"\fill[peHalvany!40] ({x0},{top}) rectangle ({x0 + m * cw},{top - n * rh});")
for i in range(n + 1):
    o.append(rf"\draw[peVilagos] ({x0 - 6.0},{top - i * rh}) -- ({x0 + m * cw + 3.1},{top - i * rh});")
for j in range(m + 1):
    o.append(rf"\draw[peVilagos] ({x0 + j * cw},{top + hh}) -- ({x0 + j * cw},{top - n * rh - 2.6});")
# elvárások és fontosság
o.append(rf"\node[font=\cimbetu\scriptsize, text=peSotet, anchor=south west] at ({x0 - 6.0},{top + 0.05}) {{VEVŐI ELVÁRÁSOK}};")
o.append(rf"\node[font=\scriptsize\bfseries, text=peSotet, rotate=90, anchor=west] at ({x0 - 0.45},{top + 0.1}) {{fontosság}};")
for i, e in enumerate(E):
    o.append(rf"\node[font=\scriptsize, anchor=west, text width=52mm] at ({x0 - 6.0},{Y(i)}) {{{e['kod']} {e['nev']}}};")
    o.append(rf"\node[font=\scriptsize\bfseries] at ({x0 - 0.45},{Y(i)}) {{{e['fontossag']}}};")
o.append(rf"\draw[peSzurke] ({x0 - 0.9},{top + hh}) -- ({x0 - 0.9},{top - n * rh});")
# jellemzők fejléce
for j, t in enumerate(M):
    nyil = r"$\uparrow$" if t["irany"] == "max" else r"$\downarrow$"
    o.append(rf"\node[font=\scriptsize, rotate=90, anchor=west, text width=36mm] at ({X(j)},{top + 0.45}) {{{t['kod']} {t['nev']}}};")
    o.append(rf"\node[font=\small, text=peKiemel] at ({X(j)},{top + 0.2}) {{{nyil}}};")
# kapcsolati jelek
for i in range(n):
    for j in range(m):
        v = R[i][j]
        x, y = X(j), Y(i)
        if v == 9:
            o.append(rf"\fill[peSotet] ({x},{y}) circle (0.17);")
        elif v == 3:
            o.append(rf"\draw[peSotet, line width=0.9pt] ({x},{y}) circle (0.16);")
        elif v == 1:
            o.append(rf"\draw[peSotet, line width=0.8pt] ({x},{y + 0.17}) -- ({x - 0.17},{y - 0.12}) -- ({x + 0.17},{y - 0.12}) -- cycle;")
# tető
ty = top + hh
o.append(rf"\draw[peKek, line width=0.8pt] ({x0},{ty}) -- ({x0 + m * cw / 2},{ty + m * cw / 2}) -- ({x0 + m * cw},{ty}) -- cycle;")
for a in range(m):
    for b in range(a + 1, m):
        cx = (X(a) + X(b)) / 2
        cy = ty + (b - a) * cw / 2
        s = cw / 2
        o.append(rf"\draw[peVilagos, line width=0.3pt] ({cx},{cy - s}) -- ({cx + s},{cy}) -- ({cx},{cy + s}) -- ({cx - s},{cy}) -- cycle;")
idx = {t["kod"]: k for k, t in enumerate(M)}
for t in d["tetokapcsolat"]:
    a, b = sorted((idx[t["a"]], idx[t["b"]]))
    cx = (X(a) + X(b)) / 2
    cy = ty + (b - a) * cw / 2
    szin = "peZold" if "+" in t["jel"] else "pePiros"
    jel = {"+": "+", "-": r"$-$", "--": r"$=$"}[t["jel"]]
    o.append(rf"\node[font=\small\bfseries, text={szin}] at ({cx},{cy}) {{{jel}}};")
o.append(rf"\node[font=\cimbetu\scriptsize, text=peKek, anchor=south] at ({x0 + m * cw / 2},{ty + m * cw / 2 + 0.1}) {{A MŰSZAKI JELLEMZŐK KÖLCSÖNHATÁSA}};")
# versenytárs-értékelés
xr = x0 + m * cw + 0.25
o.append(rf"\node[font=\cimbetu\scriptsize, text=peSotet, anchor=south west, text width=30mm] at ({xr - 0.1},{top + 0.6}) {{VEVŐI ÉRTÉKELÉS (1–5)}};")
for k, (kul, nev, szin) in enumerate([("sajat", "saját", "peKiemel"), ("A", "A", "peKek"), ("B", "B", "peLila")]):
    o.append(rf"\node[font=\scriptsize\bfseries, text={szin}] at ({xr + 0.45 + k * 0.9},{top + 0.25}) {{{nev}}};")
    for i, e in enumerate(E):
        o.append(rf"\node[font=\scriptsize, text={szin}] at ({xr + 0.45 + k * 0.9},{Y(i)}) {{{e[kul]}}};")
# alsó sorok
labels = [("abszolút fontosság", [str(v) for v in imp]),
          ("relatív fontosság [\\%]", [f"{100 * v / tot:.1f}".replace(".", ",") for v in imp]),
          ("célérték", [t["cel"] for t in M]),
          ("mértékegység", [t["egyseg"] for t in M])]
for k, (lab, vals) in enumerate(labels):
    y = top - n * rh - 0.32 - k * 0.6
    o.append(rf"\node[font=\scriptsize\bfseries, anchor=east] at ({x0 - 0.1},{y}) {{{lab}}};")
    for j, v in enumerate(vals):
        kiem = r"\bfseries" if k == 1 and imp[j] == max(imp) else ""
        o.append(rf"\node[font=\tiny{kiem}, text width=9mm, align=center] at ({X(j)},{y}) {{{v}}};")
# jelmagyarázat
ly = top - n * rh - 3.15
o.append(rf"\fill[peSotet] ({x0 - 5.8},{ly}) circle (0.14); \node[font=\scriptsize, anchor=west] at ({x0 - 5.55},{ly}) {{erős (9)}};")
o.append(rf"\draw[peSotet, line width=0.9pt] ({x0 - 3.9},{ly}) circle (0.13); \node[font=\scriptsize, anchor=west] at ({x0 - 3.65},{ly}) {{közepes (3)}};")
o.append(rf"\draw[peSotet, line width=0.8pt] ({x0 - 1.7},{ly + 0.14}) -- ({x0 - 1.84},{ly - 0.1}) -- ({x0 - 1.56},{ly - 0.1}) -- cycle; \node[font=\scriptsize, anchor=west] at ({x0 - 1.45},{ly}) {{gyenge (1)}};")
o.append(rf"\node[font=\scriptsize, anchor=west] at ({x0 + 0.6},{ly}) {{tető: {{\color{{peZold}}\bfseries +}} támogatja, {{\color{{pePiros}}\bfseries $-$}} gyengíti, {{\color{{pePiros}}\bfseries $=$}} erősen gyengíti egymást; $\uparrow$ nagyobb, $\downarrow$ kisebb a jobb}};")
o += [r"\end{tikzpicture}", r"\end{document}"]
(Path(__file__).resolve().parent / "tikz" / "qfd-bringa.tex").write_text("\n".join(o), encoding="utf-8")
print("kész: qfd-bringa.tex", imp, tot)
