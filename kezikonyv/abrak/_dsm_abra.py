#!/usr/bin/env python3
"""A VárosiBringa DSM-ábrája (eredeti és klaszterezett sorrend) a közös adatfájlból.

Futtatás: python3 kezikonyv/abrak/_dsm_abra.py  →  tikz/dsm-bringa.tex
A klaszterezés: átlagos kapcsolású hierarchikus klaszterezés a szomszédsági halmazok
Jaccard-távolságán (ugyanaz, mint a Gyakorlati útmutató n2_dsm notebookjában).
"""
import json
from pathlib import Path

import numpy as np
from scipy.cluster.hierarchy import fcluster, leaves_list, linkage
from scipy.spatial.distance import squareform

GY = Path(__file__).resolve().parents[2]
d = json.loads((GY / "_shared" / "adat" / "dsm_bringa.json").read_text(encoding="utf-8"))
kod = [e["kod"] for e in d["elemek"]]
nev = {e["kod"]: e["nev"] for e in d["elemek"]}
n = len(kod)
I = {c: i for i, c in enumerate(kod)}
A = np.zeros((n, n), int)
for a, b in d["kapcsolatok"]:
    A[I[a], I[b]] = A[I[b], I[a]] = 1
N = [set(np.flatnonzero(A[i])) | {i} for i in range(n)]
D = np.array([[1 - len(N[i] & N[j]) / len(N[i] | N[j]) for j in range(n)] for i in range(n)])
Z = linkage(squareform(D, checks=False), "average")
cl = fcluster(Z, 3, "maxclust")
rend = list(leaves_list(Z))
c = 0.42  # cellaméret


def matrix(o, x0, rendezes, cim, klaszterek=False):
    o.append(rf"\node[font=\cimbetu\small, text=peSotet, anchor=south] at ({x0 + n * c / 2},{0.95}) {{{cim}}};")
    for k_, i in enumerate(rendezes):
        y = -(k_ + 0.5) * c
        o.append(rf"\node[font=\tiny, anchor=east] at ({x0 - 0.08},{y}) {{{nev[kod[i]]} ({kod[i]})}};")
        o.append(rf"\node[font=\tiny, rotate=90, anchor=west] at ({x0 + (k_ + 0.5) * c},{0.05}) {{{kod[i]}}};")
    for a_, i in enumerate(rendezes):
        for b_, j in enumerate(rendezes):
            x, y = x0 + b_ * c, -(a_ + 1) * c
            if i == j:
                o.append(rf"\fill[peSotet] ({x},{y}) rectangle ({x + c},{y + c});")
            elif A[i, j]:
                o.append(rf"\fill[peKozep] ({x + 0.05},{y + 0.05}) rectangle ({x + c - 0.05},{y + c - 0.05});")
    for k_ in range(n + 1):
        o.append(rf"\draw[peVilagos, line width=0.3pt] ({x0},{-k_ * c}) -- ({x0 + n * c},{-k_ * c});")
        o.append(rf"\draw[peVilagos, line width=0.3pt] ({x0 + k_ * c},0) -- ({x0 + k_ * c},{-n * c});")
    if klaszterek:
        k_ = 0
        szinek = ["peKiemel", "peZold", "peLila"]
        for s, cid in enumerate(dict.fromkeys(cl[i] for i in rendezes)):
            m = sum(1 for i in rendezes if cl[i] == cid)
            o.append(rf"\draw[{szinek[s % 3]}, line width=1.4pt] ({x0 + k_ * c},{-k_ * c}) rectangle ({x0 + (k_ + m) * c},{-(k_ + m) * c});")
            k_ += m


o = [r"\documentclass[tikz,border=6pt]{standalone}", r"\usepackage{peabra}", r"\begin{document}",
     r"\begin{tikzpicture}[x=1cm,y=1cm]"]
matrix(o, 0, list(range(n)), "a) eredeti sorrend")
matrix(o, n * c + 4.2, rend, "b) klaszterezett sorrend: három modul", klaszterek=True)
kereszt = sum(A[i, j] for i in range(n) for j in range(i + 1, n) if cl[i] != cl[j])
o.append(rf"\node[felirat, text width=150mm, align=center] at ({n * c + 2.1},{-n * c - 0.55}) "
         rf"{{A {A.sum() // 2} kapcsolatból {kereszt} esik a modulok közé; ezek a modulinterfészek. "
         rf"Narancs: platform (szoftver) $\cdot$ zöld: dokkoló $\cdot$ lila: kerékpár.}};")
o += [r"\end{tikzpicture}", r"\end{document}"]
(Path(__file__).resolve().parent / "tikz" / "dsm-bringa.tex").write_text("\n".join(o), encoding="utf-8")
print("kész: dsm-bringa.tex", [kod[i] for i in rend], "kereszt:", kereszt)
