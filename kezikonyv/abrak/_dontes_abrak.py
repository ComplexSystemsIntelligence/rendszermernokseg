#!/usr/bin/env python3
"""A 10. fejezet generált ábrái a közös adatfájlokból.

pareto-bringa.tex: a VárosiBringa tervváltozatai és a Pareto-front (_shared/adat/pareto_bringa.json)
erzekenyseg-kobo.tex: a KoboCella súlyozott értékelésének érzékenysége a K5 súlyára (_shared/adat/dontes_kobo.json)
"""
import json
from pathlib import Path

GY = Path(__file__).resolve().parents[2]
T = Path(__file__).resolve().parent / "tikz"
FEJ = [r"\documentclass[tikz,border=6pt]{standalone}", r"\usepackage{peabra}", r"\begin{document}"]

# --- Pareto-front ---
d = json.loads((GY / "_shared/adat/pareto_bringa.json").read_text(encoding="utf-8"))["valtozatok"]
def dominalt(a):
    return any(b["koltseg"] <= a["koltseg"] and b["elerhetoseg"] >= a["elerhetoseg"] and
               (b["koltseg"] < a["koltseg"] or b["elerhetoseg"] > a["elerhetoseg"]) for b in d)
nd = sorted([a for a in d if not dominalt(a)], key=lambda a: a["koltseg"])
o = FEJ + [r"\begin{tikzpicture}", r"\begin{axis}[width=13cm, height=8cm, xmin=58, xmax=96, ymin=84, ymax=98.5,"
           r" xlabel={éves költség [MFt/év] (kisebb a jobb)}, ylabel={elérhetőség [\%] (nagyobb a jobb)},"
           r" grid=both, grid style={peVilagos!60, line width=0.3pt}, tick label style={font=\footnotesize},"
           r" label style={font=\footnotesize}, axis line style={peSotet}]"]
o.append(r"\addplot[peKiemel, line width=1.4pt, mark=none] coordinates {" + " ".join(f"({a['koltseg']},{a['elerhetoseg']})" for a in nd) + "};")
o.append(r"\addplot[draw=peSotet, fill=peSzurkeH, mark=*, only marks, mark size=3pt] coordinates {" +
         " ".join(f"({a['koltseg']},{a['elerhetoseg']})" for a in d if dominalt(a)) + "};")
o.append(r"\addplot[draw=peKiemel, fill=peKiemel, mark=*, only marks, mark size=3.4pt] coordinates {" +
         " ".join(f"({a['koltseg']},{a['elerhetoseg']})" for a in nd) + "};")
for a in d:
    pos = "above left" if not dominalt(a) else "below right"
    o.append(rf"\node[font=\scriptsize, {pos}, inner sep=2pt] at (axis cs:{a['koltseg']},{a['elerhetoseg']}) {{{a['kod']}}};")
o.append(r"\draw[peKek, dash pattern=on 4pt off 2pt, line width=0.9pt] (axis cs:80,84) -- (axis cs:80,98.5) node[pos=0.06, left, font=\scriptsize, text=peKek, align=right] {költségkeret\\80 MFt/év};")
o.append(r"\node[font=\scriptsize, text=peKiemel, anchor=west] at (axis cs:86.5,96.2) {Pareto-front};")
o += [r"\end{axis}", r"\end{tikzpicture}", r"\end{document}"]
(T / "pareto-bringa.tex").write_text("\n".join(o), encoding="utf-8")

# --- Érzékenység ---
k = json.loads((GY / "_shared/adat/dontes_kobo.json").read_text(encoding="utf-8"))["sulyozott"]
alts = k["alternativak"]
def hasznossag(kr, x):
    if "skala" in kr:
        return kr["skala"][x]
    return round(10 * (kr["rossz"] - x) / (kr["rossz"] - kr["jo"]), 1)
U = {kr["kod"]: [hasznossag(kr, x) for x in kr["ertekek"]] for kr in k["kriteriumok"]}
W = {kr["kod"]: kr["suly"] for kr in k["kriteriumok"]}
def pont(kk, w):
    Wn = {c: (W[c] * (100 - w) / (100 - W[kk]) if c != kk else w) for c in W}
    return [sum(Wn[c] * U[c][i] for c in W) / 100 for i in range(len(alts))]
nevek = json.loads((GY / "_shared/adat/dontes_kobo.json").read_text(encoding="utf-8"))["alternativak"]
szin = {"A": "peKek", "B": "peKiemel", "D": "peZold"}
o = FEJ + [r"\begin{tikzpicture}", r"\begin{axis}[width=12.5cm, height=7cm, xmin=0, xmax=50, ymin=5.5, ymax=8.2,"
           r" xlabel={a K5 (átállási idő) kritérium súlya}, ylabel={súlyozott pontszám (0--10)},"
           r" grid=both, grid style={peVilagos!60, line width=0.3pt}, tick label style={font=\footnotesize},"
           r" label style={font=\footnotesize}, legend style={font=\scriptsize, at={(0.98,0.03)}, anchor=south east, draw=peVilagos}]"]
for i, a in enumerate(alts):
    pts = " ".join(f"({w},{pont('K5', w)[i]:.3f})" for w in range(0, 51, 1))
    o.append(rf"\addplot[{szin[a]}, line width=1.3pt, mark=none] coordinates {{{pts}}};")
    o.append(rf"\addlegendentry{{{a}: {nevek[a]}}}")
o.append(r"\draw[peSzurke, dash pattern=on 3pt off 2pt] (axis cs:15,5.5) -- (axis cs:15,8.2) node[pos=0.97, right, font=\scriptsize, text=peSotet] {alapsúly: 15};")
o.append(r"\draw[pePiros, dash pattern=on 3pt off 2pt] (axis cs:7.6,5.5) -- (axis cs:7.6,8.2) node[pos=0.88, left, font=\scriptsize, text=pePiros, align=right] {váltás:\\7,6};")
o += [r"\end{axis}", r"\end{tikzpicture}", r"\end{document}"]
(T / "erzekenyseg-kobo.tex").write_text("\n".join(o), encoding="utf-8")
print("kész: pareto-bringa.tex, erzekenyseg-kobo.tex; front:", [a["kod"] for a in nd])
