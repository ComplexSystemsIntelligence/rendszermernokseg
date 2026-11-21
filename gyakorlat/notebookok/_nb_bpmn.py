from _kozos import BETOLTO, code, fejresz, md

NEV = "bpmn"
CIM = "BPMN-modell táblázatból: szerkezeti ellenőrzés, BPMN 2.0 XML export, ciklusidő-szimuláció és eseménynapló"

CELLAK = [
    fejresz(NEV, CIM, """
A notebook

1. az elemek, a kapcsolatok és a sávok táblázatából felépíti a folyamatmodellt, és szerkezetileg ellenőrzi (elérhetőség, átjárók, valószínűségek);
2. szabványos BPMN 2.0 XML-fájlt készít diagramadatokkal, amely a bpmn.io webes szerkesztőjében vagy más BPMN-eszközben megnyitható és tovább szerkeszthető;
3. Monte Carlo-szimulációval kiszámítja a ciklusidő eloszlását (a kizáró átjárók valószínűségeivel, a párhuzamos ágak leghosszabbikával, az ismétlésekkel);
4. eseménynaplót generál, és megmutatja a leggyakoribb folyamatváltozatokat (a folyamatbányászat bemenete).

A beépített példa a ForgácsTech rendelésteljesítési folyamatának jövőbeli modellje (kézikönyv 20. fejezet; OMG, 2011; Dumas és mtsai, 2018).
""", sablon="bpmn_sablon.xlsx", eszkozlap="Gyakorlati útmutató, BPMN-modellezés eszközlap"),
    code('''
SAJAT_SABLON = False   # True: a kitöltött bpmn_sablon.xlsx
CV = 0.3               # a tevékenységidők relatív szórása a szimulációban
ESETEK = 5000
''' + BETOLTO + '''
import textwrap
import unicodedata
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, Rectangle
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET
'''),
    md("## Adatok"),
    code('''
if SAJAT_SABLON:
    fajl = sablon_betoltese("bpmn_sablon.xlsx")
    savok = pd.read_excel(fajl, sheet_name="Sávok", header=2).iloc[:, :3]
    savok.columns = ["sav", "medence", "sorrend"]
    elemek = pd.read_excel(fajl, sheet_name="Elemek", header=2).iloc[:, :7]
    elemek.columns = ["id", "tipus", "nev", "sav", "oszlop", "ido", "ftip"]
    kapcs = pd.read_excel(fajl, sheet_name="Kapcsolatok", header=2).iloc[:, :6]
    kapcs.columns = ["id", "honnan", "hova", "tipus", "cimke", "p"]
    fa = pd.read_excel(fajl, sheet_name="Folyamatáram", header=None)
    sor = fa.index[fa.iloc[:, 0].astype(str).str.startswith("Átlagos ciklusidő [óra]")]
    ANALITIKUS = float(fa.iloc[sor[0], 8]) if len(sor) else np.nan
else:
    savok = pd.DataFrame([("Vevő", "Vevő", 0), ("értékesítés", "ForgácsTech", 1), ("gyártáselőkészítés", "ForgácsTech", 2),
                          ("gyártás", "ForgácsTech", 3), ("minőségügy, expediálás", "ForgácsTech", 4)], columns=["sav", "medence", "sorrend"])
    elemek = pd.DataFrame([
        ("VEVO", "külső résztvevő", "Vevő", "Vevő", None, None, ""), ("S", "indító esemény", "rendelés beérkezett", "értékesítés", 1, 0, ""),
        ("T1", "feladat", "rendelés rögzítése a MES-ben", "értékesítés", 2, 0.5, "felhasználói"),
        ("T2", "feladat", "kapacitás és anyag ellenőrzése", "gyártáselőkészítés", 2, 2, "felhasználói"),
        ("G1", "XOR", "tartható a határidő?", "gyártáselőkészítés", 3, 0, ""), ("T3", "feladat", "új határidő egyeztetése", "értékesítés", 3, 24, "felhasználói"),
        ("M1", "XOR", "", "értékesítés", 4, 0, ""), ("T4", "feladat", "visszaigazolás küldése", "értékesítés", 5, 0.5, "üzenetküldő"),
        ("A1", "ÉS", "", "gyártáselőkészítés", 5, 0, ""), ("T5", "feladat", "CAM-program, technológia", "gyártáselőkészítés", 6, 6, "felhasználói"),
        ("T6", "feladat", "anyag lefoglalása, előkészítése", "gyártás", 6, 4, "kézi"), ("A2", "ÉS", "", "gyártáselőkészítés", 7, 0, ""),
        ("T7", "feladat", "rendelés kiadása a gépre", "gyártáselőkészítés", 8, 22.5, "felhasználói"), ("T8", "feladat", "megmunkálás", "gyártás", 8, 2.5, "kézi"),
        ("T9", "feladat", "sorjázás, mosás", "gyártás", 9, 8.0, "kézi"), ("M2", "XOR", "", "minőségügy, expediálás", 10, 0, ""),
        ("T10", "feladat", "minőségellenőrzés", "minőségügy, expediálás", 11, 8.1, "kézi"), ("G2", "XOR", "megfelelő?", "minőségügy, expediálás", 12, 0, ""),
        ("T11", "feladat", "utómunka", "gyártás", 12, 2, "kézi"), ("T12", "feladat", "csomagolás, kiszállítás", "minőségügy, expediálás", 13, 7.9, "kézi"),
        ("E", "záró esemény", "rendelés teljesítve", "minőségügy, expediálás", 14, 0, "")], columns=["id", "tipus", "nev", "sav", "oszlop", "ido", "ftip"])
    k = [("S", "T1"), ("T1", "T2"), ("T2", "G1"), ("G1", "T3", "nem", 0.2), ("G1", "M1", "igen", 0.8), ("T3", "M1"), ("M1", "T4"), ("T4", "A1"),
         ("A1", "T5"), ("A1", "T6"), ("T5", "A2"), ("T6", "A2"), ("A2", "T7"), ("T7", "T8"), ("T8", "T9"), ("T9", "M2"), ("M2", "T10"),
         ("T10", "G2"), ("G2", "T11", "nem", 0.05), ("G2", "T12", "igen", 0.95), ("T11", "M2"), ("T12", "E")]
    kapcs = pd.DataFrame([(f"F{i + 1}", a[0], a[1], "szekvencia", a[2] if len(a) > 2 else "", a[3] if len(a) > 3 else np.nan) for i, a in enumerate(k)]
                         + [("U1", "VEVO", "S", "üzenet", "rendelés", np.nan), ("U2", "T3", "VEVO", "üzenet", "határidő-javaslat", np.nan),
                            ("U3", "T4", "VEVO", "üzenet", "visszaigazolás", np.nan), ("U4", "T12", "VEVO", "üzenet", "termék, szállítólevél", np.nan)],
                         columns=["id", "honnan", "hova", "tipus", "cimke", "p"])
    ANALITIKUS = 63.33
savok = savok[savok.sav.notna()].sort_values("sorrend").reset_index(drop=True)
elemek = elemek[elemek.id.notna()].copy()
for c in ("id", "tipus", "nev", "sav", "ftip"):
    elemek[c] = elemek[c].fillna("").astype(str).str.strip()
elemek["ido"] = pd.to_numeric(elemek.ido, errors="coerce").fillna(0)
elemek["oszlop"] = pd.to_numeric(elemek.oszlop, errors="coerce")
kapcs = kapcs[kapcs.id.notna() & kapcs.honnan.notna()].copy()
for c in ("id", "honnan", "hova", "tipus", "cimke"):
    kapcs[c] = kapcs[c].fillna("").astype(str).str.strip()
kapcs["p"] = pd.to_numeric(kapcs.p, errors="coerce")
E = elemek.set_index("id")
print(f"{len(savok)} sáv, {len(elemek)} elem, {len(kapcs)} kapcsolat")
'''),
    md("## Szerkezeti ellenőrzés"),
    code('''
belso = elemek[elemek.tipus != "külső résztvevő"]
seq = kapcs[kapcs.tipus == "szekvencia"]
G = nx.DiGraph()
G.add_nodes_from(belso.id)
for _, f in seq.iterrows():
    G.add_edge(f.honnan, f.hova, p=f.p, cimke=f.cimke, id=f.id)
starts = belso.id[belso.tipus == "indító esemény"].tolist()
ends = belso.id[belso.tipus == "záró esemény"].tolist()
hibak = []
if len(starts) != 1: hibak.append(f"{len(starts)} indító esemény (egy ajánlott)")
if len(ends) != 1: hibak.append(f"{len(ends)} záró esemény (egy ajánlott)")
elerheto = set().union(*[nx.descendants(G, s) | {s} for s in starts]) if starts else set()
nem_elerheto = set(G.nodes) - elerheto
if nem_elerheto: hibak.append(f"az indító eseményből nem érhető el: {sorted(nem_elerheto)}")
zsakutca = [n for n in G.nodes if not any(nx.has_path(G, n, e) for e in ends)]
if zsakutca: hibak.append(f"nem vezet záró eseményhez: {sorted(zsakutca)}")
for n in G.nodes:
    t = E.loc[n, "tipus"]
    if t in ("feladat", "alfolyamat") and (G.in_degree(n) > 1 or G.out_degree(n) > 1):
        hibak.append(f"{n}: több be- vagy kimenet egy feladaton")
    if t in ("XOR", "ÉS", "VAGY") and G.in_degree(n) > 1 and G.out_degree(n) > 1:
        hibak.append(f"{n}: vegyes átjáró")
    if t == "XOR" and G.out_degree(n) > 1:
        ps = [G.edges[n, s]["p"] for s in G.successors(n)]
        if any(pd.isna(p) for p in ps) or abs(sum(ps) - 1) > 1e-6:
            hibak.append(f"{n}: a kimenő ágak valószínűsége hiányzik vagy nem 1 az összege")
print("Szerkezeti hibák:", hibak or "nincs")
print(f"Elemek: {len(belso)} (50 fölött bontsd alfolyamatokra); feladatok: {int(belso.tipus.isin(['feladat', 'alfolyamat']).sum())}; "
      f"VAGY átjárók: {int((belso.tipus == 'VAGY').sum())}")
'''),
    md("## Elrendezés és BPMN 2.0 XML"),
    code('''
SH, EXT_H, HEAD, COLW, X0 = 120, 70, 30, 150, 110
meret = {"feladat": (100, 70), "alfolyamat": (100, 70), "XOR": (50, 50), "ÉS": (50, 50), "VAGY": (50, 50),
         "indító esemény": (36, 36), "záró esemény": (36, 36), "köztes esemény": (36, 36)}
medence_of = dict(zip(savok.sav, savok.medence))
kulso_medencek = [m for m in savok.medence.unique() if set(elemek.tipus[elemek.sav.map(medence_of) == m]) <= {"külső résztvevő"}]
# sávok függőleges helye
y, sav_y = 0, {}
for _, s in savok.iterrows():
    h = EXT_H if s.medence in kulso_medencek else SH
    sav_y[s.sav] = (y, h); y += h + (20 if s.medence in kulso_medencek else 0)
HT = y
oszl_max = int(np.nanmax(elemek.oszlop)) if elemek.oszlop.notna().any() else len(elemek)
W = X0 + oszl_max * COLW + 60
pos = {}
for i, e in belso.reset_index(drop=True).iterrows():
    ox = e.oszlop if pd.notna(e.oszlop) else i + 1
    y0, h = sav_y[e.sav]
    w, hh = meret.get(e.tipus, (100, 70))
    pos[e.id] = (X0 + (ox - 1) * COLW + 60, y0 + h / 2, w, hh)

def hatar(n, irany):
    x, y, w, h = pos[n]
    return {"jobb": (x + w / 2, y), "bal": (x - w / 2, y), "fent": (x, y - h / 2), "lent": (x, y + h / 2)}[irany]

def utvonal(a, b):
    ax, ay, _, _ = pos[a]; bx, by, _, _ = pos[b]
    if abs(ay - by) < 1:
        if bx > ax: return [hatar(a, "jobb"), hatar(b, "bal")]
        top = min(ay - pos[a][3] / 2, by - pos[b][3] / 2) - 25
        return [hatar(a, "fent"), (ax, top), (bx, top), hatar(b, "fent")]
    le = by > ay
    if abs(ax - bx) < 1:
        return [hatar(a, "lent" if le else "fent"), hatar(b, "fent" if le else "lent")]
    # előbb függőlegesen, ha a forrás oszlopában a cél sávja szabad; különben előbb vízszintesen
    szabad = not any(abs(pos[n][0] - ax) < 1 and abs(pos[n][1] - by) < 1 for n in pos if n != b)
    if szabad:
        return [hatar(a, "lent" if le else "fent"), (ax, by), hatar(b, "bal" if bx > ax else "jobb")]
    kezdo = hatar(a, "jobb" if bx > ax else "bal")
    return [kezdo, (bx, ay), hatar(b, "fent" if le else "lent")]

def uzenet_ut(f):
    if f.honnan in pos and f.hova in pos:
        return utvonal(f.honnan, f.hova)
    belso_id, kulso = (f.honnan, f.hova) if f.honnan in pos else (f.hova, f.honnan)
    x, y, w, h = pos[belso_id]
    y0, hk = sav_y[E.loc[kulso, "sav"]]
    fent = y0 < y
    a = (x, y - h / 2) if fent else (x, y + h / 2)
    b = (x, y0 + hk) if fent else (x, y0)
    return [a, b] if f.honnan in pos else [b, a]

XMLTIP = {"indító esemény": "startEvent", "záró esemény": "endEvent", "köztes esemény": "intermediateThrowEvent",
          "alfolyamat": "subProcess", "XOR": "exclusiveGateway", "ÉS": "parallelGateway", "VAGY": "inclusiveGateway"}
FTIPX = {"felhasználói": "userTask", "automatikus": "serviceTask", "kézi": "manualTask", "üzenetküldő": "sendTask"}
def xid(s):
    # a BPMN-azonosító ASCII NCName kell legyen: ékezet nélkül, csak betű, szám, aláhúzás
    s = "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c))
    return "id_" + "".join(c if (c.isascii() and c.isalnum()) else "_" for c in s)
belso_medencek = [m for m in savok.medence.unique() if m not in kulso_medencek]
uz_cel = set(kapcs.hova[kapcs.tipus == "üzenet"])
L = ['<?xml version="1.0" encoding="UTF-8"?>',
     '<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" '
     'xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_1" '
     'targetNamespace="http://bpmn.io/schema/bpmn">', '  <bpmn:collaboration id="Collaboration_1">']
resztvevo = {}
for m in belso_medencek:
    resztvevo[m] = xid("P_" + m)
    L.append(f'    <bpmn:participant id="{resztvevo[m]}" name="{escape(m)}" processRef="{xid("Proc_" + m)}"/>')
for m in kulso_medencek:
    resztvevo[m] = xid("P_" + m)
    L.append(f'    <bpmn:participant id="{resztvevo[m]}" name="{escape(m)}"/>')
def ref(n):
    return resztvevo[medence_of[E.loc[n, "sav"]]] if E.loc[n, "tipus"] == "külső résztvevő" else xid(n)
for _, f in kapcs[kapcs.tipus == "üzenet"].iterrows():
    L.append(f'    <bpmn:messageFlow id="{xid(f.id)}" name="{escape(f.cimke)}" sourceRef="{ref(f.honnan)}" targetRef="{ref(f.hova)}"/>')
L.append("  </bpmn:collaboration>")
for m in belso_medencek:
    L.append(f'  <bpmn:process id="{xid("Proc_" + m)}" isExecutable="false">')
    L.append(f'    <bpmn:laneSet id="{xid("LS_" + m)}">')
    for s in savok.sav[savok.medence == m]:
        L.append(f'      <bpmn:lane id="{xid("L_" + s)}" name="{escape(s)}">')
        L += [f'        <bpmn:flowNodeRef>{xid(n)}</bpmn:flowNodeRef>' for n in belso.id[belso.sav == s]]
        L.append("      </bpmn:lane>")
    L.append("    </bpmn:laneSet>")
    for _, e in belso[belso.sav.map(medence_of) == m].iterrows():
        tag = FTIPX.get(e.ftip, "task") if e.tipus == "feladat" else XMLTIP.get(e.tipus, "task")
        L.append(f'    <bpmn:{tag} id="{xid(e.id)}" name="{escape(e.nev)}">')
        L += [f'      <bpmn:incoming>{xid(f)}</bpmn:incoming>' for f in seq.id[seq.hova == e.id]]
        L += [f'      <bpmn:outgoing>{xid(f)}</bpmn:outgoing>' for f in seq.id[seq.honnan == e.id]]
        if e.tipus == "indító esemény" and e.id in uz_cel:
            L.append(f'      <bpmn:messageEventDefinition id="{xid("MED_" + e.id)}"/>')
        L.append(f"    </bpmn:{tag}>")
    for _, f in seq[seq.honnan.isin(belso.id[belso.sav.map(medence_of) == m])].iterrows():
        L.append(f'    <bpmn:sequenceFlow id="{xid(f.id)}" name="{escape(f.cimke)}" sourceRef="{xid(f.honnan)}" targetRef="{xid(f.hova)}"/>')
    L.append("  </bpmn:process>")
L += ['  <bpmndi:BPMNDiagram id="Diagram_1">', '    <bpmndi:BPMNPlane id="Plane_1" bpmnElement="Collaboration_1">']
def bounds(x, y, w, h):
    return f'<dc:Bounds x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}"/>'
for m in belso_medencek + kulso_medencek:
    ss = savok.sav[savok.medence == m].tolist()
    y0 = sav_y[ss[0]][0]; y1 = sav_y[ss[-1]][0] + sav_y[ss[-1]][1]
    L.append(f'      <bpmndi:BPMNShape id="{resztvevo[m]}_di" bpmnElement="{resztvevo[m]}" isHorizontal="true">{bounds(0, y0, W, y1 - y0)}</bpmndi:BPMNShape>')
    if m in belso_medencek:
        for s in ss:
            L.append(f'      <bpmndi:BPMNShape id="{xid("L_" + s)}_di" bpmnElement="{xid("L_" + s)}" isHorizontal="true">{bounds(HEAD, sav_y[s][0], W - HEAD, sav_y[s][1])}</bpmndi:BPMNShape>')
for n, (x, y, w, h) in pos.items():
    extra = ' isMarkerVisible="true"' if E.loc[n, "tipus"] == "XOR" else ""
    L.append(f'      <bpmndi:BPMNShape id="{xid(n)}_di" bpmnElement="{xid(n)}"{extra}>{bounds(x - w / 2, y - h / 2, w, h)}</bpmndi:BPMNShape>')
for _, f in kapcs.iterrows():
    pts = utvonal(f.honnan, f.hova) if f.tipus == "szekvencia" else uzenet_ut(f)
    wp = "".join(f'<di:waypoint x="{px:.0f}" y="{py:.0f}"/>' for px, py in pts)
    L.append(f'      <bpmndi:BPMNEdge id="{xid(f.id)}_di" bpmnElement="{xid(f.id)}">{wp}</bpmndi:BPMNEdge>')
L += ["    </bpmndi:BPMNPlane>", "  </bpmndi:BPMNDiagram>", "</bpmn:definitions>"]
xml = "\\n".join(L)
gyoker = ET.fromstring(xml.encode("utf-8"))   # jól formázott-e?
idk = {el.get("id") for el in gyoker.iter() if el.get("id")}
hivatk = {el.get(a) for el in gyoker.iter() for a in ("sourceRef", "targetRef", "processRef", "bpmnElement") if el.get(a)}
assert hivatk <= idk, f"feloldatlan hivatkozás: {hivatk - idk}"
with open("folyamat.bpmn", "w", encoding="utf-8") as fh:
    fh.write(xml)
print(f"folyamat.bpmn elkészült ({len(xml) // 1024} kB, {len(idk)} azonosító); megnyitás: https://demo.bpmn.io → Open (fájl feltöltése)")
'''),
    md("## Ciklusidő-szimuláció és eseménynapló"),
    code('''
rng = np.random.default_rng(7)
def ido(m):
    if m <= 0: return 0.0
    s = np.sqrt(np.log(1 + CV ** 2))
    return float(rng.lognormal(np.log(m) - s ** 2 / 2, s))
# a párhuzamos (és befogadó) elágazások összefutó párja: a minden ágból elérhető legközelebbi összefutó átjáró
PAR = {}
for n in G.nodes:
    if E.loc[n, "tipus"] in ("ÉS", "VAGY") and G.out_degree(n) > 1:
        tav = [nx.single_source_shortest_path_length(G, s) for s in G.successors(n)]
        jel = [j for j in G.nodes if E.loc[j, "tipus"] == E.loc[n, "tipus"] and G.in_degree(j) > 1 and all(j in t for t in tav)]
        PAR[n] = min(jel, key=lambda j: max(t[j] for t in tav))

def futtat(node, t, stop, napló):
    lepes = 0
    while node != stop:
        lepes += 1
        if lepes > 10000: raise RuntimeError("végtelen ciklus?")
        e = E.loc[node]
        if e.tipus in ("feladat", "alfolyamat"):
            d = ido(e.ido); napló.append((e.nev, e.sav, t, t + d)); t += d
        succ = list(G.successors(node))
        if e.tipus == "záró esemény" or not succ:
            return t
        if node in PAR:
            join = PAR[node]
            t = max(futtat(s, t, join, napló) for s in succ)
            node = next(iter(G.successors(join)), None)
            if node is None: return t
            continue
        if e.tipus == "XOR" and len(succ) > 1:
            p = np.array([G.edges[node, s]["p"] for s in succ], float); p = p / p.sum()
            node = succ[rng.choice(len(succ), p=p)]
        else:
            node = succ[0]
    return t

kezd = pd.Timestamp("2026-01-05 06:00")
sorok, ct, valt = [], [], []
for c in range(ESETEK):
    napló = []
    t0 = c * 2.5
    t1 = futtat(starts[0], t0, None, napló)
    ct.append(t1 - t0)
    napló.sort(key=lambda r: (r[2], r[0]))
    valt.append(" → ".join(r[0] for r in napló))
    if c < 300:
        sorok += [(f"R{c + 1:04d}", a, kezd + pd.Timedelta(hours=s), kezd + pd.Timedelta(hours=v), sav) for a, sav, s, v in napló]
ct = np.array(ct)
naplo = pd.DataFrame(sorok, columns=["eset", "tevekenyseg", "kezdes", "befejezes", "eroforras"])
naplo.to_csv("esemenynaplo.csv", index=False)
print(f"Szimulált átlagos ciklusidő: {ct.mean():.1f} óra (folyamatáram-elemzés: {ANALITIKUS:.1f} óra); "
      f"medián {np.median(ct):.1f}, 90. percentilis {np.percentile(ct, 90):.1f}, 99. percentilis {np.percentile(ct, 99):.1f} óra")
vs = pd.Series(valt).value_counts(normalize=True)
print(f"{len(vs)} folyamatváltozat; a négy leggyakoribb:")
for v, a in vs.head(4).items():
    print(f"  {a:6.1%}  {textwrap.shorten(v, 160)}")
print(f"esemenynaplo.csv: {naplo.eset.nunique()} eset, {len(naplo)} esemény (a folyamatbányászati eszközlap bemenete)")
'''),
    md("## Ábra"),
    code('''
dh = 15.4 * (HT + 10) / (W + 10)
H = dh + 4.4
fig = plt.figure(figsize=(16, H))
ax = fig.add_axes([0.02, 4.2 / H, 0.96, dh / H])
for m in belso_medencek + kulso_medencek:
    ss = savok.sav[savok.medence == m].tolist()
    y0 = sav_y[ss[0]][0]; y1 = sav_y[ss[-1]][0] + sav_y[ss[-1]][1]
    ax.add_patch(Rectangle((0, y0), W, y1 - y0, fill=False, ec="#1F3A5A", lw=1.2))
    if m in kulso_medencek:
        ax.text(W / 2, (y0 + y1) / 2, m, ha="center", va="center", fontsize=10, weight="bold", color="#1F3A5A")
    else:
        ax.text(HEAD / 2, (y0 + y1) / 2, m, rotation=90, ha="center", va="center", fontsize=9, weight="bold", color="#1F3A5A")
        for s in ss:
            sy, sh = sav_y[s]
            ax.add_patch(Rectangle((HEAD, sy), W - HEAD, sh, fill=False, ec="#1F3A5A", lw=0.6))
            ax.text(HEAD + 12, sy + sh / 2, textwrap.fill(s, 12, break_long_words=False), rotation=90, ha="center", va="center", fontsize=5.5)
for _, f in kapcs.iterrows():
    pts = np.array(utvonal(f.honnan, f.hova) if f.tipus == "szekvencia" else uzenet_ut(f))
    st = dict(color="#1F3A5A", lw=1.0) if f.tipus == "szekvencia" else dict(color="#888888", lw=0.9, ls="--")
    ax.plot(pts[:, 0], pts[:, 1], **st)
    ax.annotate("", xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle="-|>" if f.tipus == "szekvencia" else "-|>", color=st["color"], lw=st["lw"],
                                                                 fc="white" if f.tipus == "üzenet" else st["color"]))
    if f.cimke and f.tipus == "szekvencia":
        ax.text(pts[0][0] + 8, pts[0][1] - 6, f.cimke, fontsize=6.5, color="#E07B39")
for n, (x, y, w, h) in pos.items():
    t = E.loc[n, "tipus"]
    if t in ("feladat", "alfolyamat"):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0,rounding_size=8", fc="#E6EEF6", ec="#285780", lw=1))
        ax.text(x, y, textwrap.fill(E.loc[n, "nev"], 13, break_long_words=False), ha="center", va="center", fontsize=6)
    elif t in ("XOR", "ÉS", "VAGY"):
        ax.add_patch(Polygon([[x, y - h / 2], [x + w / 2, y], [x, y + h / 2], [x - w / 2, y]], fc="#FBE3D2", ec="#E07B39", lw=1))
        ax.text(x, y, {"XOR": "×", "ÉS": "+", "VAGY": "○"}[t], ha="center", va="center", fontsize=13, weight="bold", color="#1F3A5A")
        if E.loc[n, "nev"]:
            ax.text(x, y + h / 2 + 4, textwrap.fill(E.loc[n, "nev"], 14), ha="center", va="top", fontsize=6)
    else:
        lw = 3 if t == "záró esemény" else 1.2
        ax.add_patch(Circle((x, y), w / 2, fc="white", ec="#B83A3A" if t == "záró esemény" else "#3E8E63", lw=lw))
ax.set_xlim(-5, W + 5); ax.set_ylim(HT + 5, -5); ax.set_aspect("equal"); ax.axis("off")
ax2 = fig.add_axes([0.06, 0.5 / H, 0.42, 3.0 / H])
ax2.hist(ct, bins=60, color="#A9C4DE")
ax2.axvline(ct.mean(), color="#285780", lw=2, label=f"átlag {ct.mean():.1f} h")
ax2.axvline(np.percentile(ct, 90), color="#E07B39", ls="--", label=f"90. percentilis {np.percentile(ct, 90):.1f} h")
ax2.set_xlabel("ciklusidő [óra]"); ax2.set_ylabel("esetek száma"); ax2.legend(fontsize=8); ax2.set_title("A ciklusidő eloszlása (szimuláció)", fontsize=10)
ax3 = fig.add_axes([0.6, 0.5 / H, 0.37, 3.0 / H])
top = vs.head(4)
alap = vs.index[0].split(" → ")
cimk = []
for v in top.index:
    lep = v.split(" → ")
    plusz = [a for a in dict.fromkeys(lep) if lep.count(a) > alap.count(a)]
    minusz = [a for a in dict.fromkeys(alap) if alap.count(a) > lep.count(a)]
    cimk.append("leggyakoribb út" if v == vs.index[0] else
                " ".join(["+ " + ", ".join(plusz) if plusz else "", "− " + ", ".join(minusz) if minusz else ""]).strip())
ax3.barh(range(len(top)), top.values * 100, color="#285780")
ax3.set_yticks(range(len(top)), [textwrap.shorten(c, 40) for c in cimk], fontsize=8); ax3.invert_yaxis()
ax3.set_xlabel("az esetek aránya [%]"); ax3.set_title("A leggyakoribb folyamatváltozatok", fontsize=10)
plt.savefig("bpmn.png", bbox_inches="tight", dpi=150); plt.show()
'''),
    md("""
## Értelmezés

- A modell szerkezetileg helyes: egy indító és egy záró esemény, minden elem elérhető, minden elágazó átjárónak van összefutó párja, a kizáró átjárók ágainak valószínűsége 1-re összegződik.
- A `folyamat.bpmn` fájl a bpmn.io szerkesztőjében megnyitható; az elrendezés az oszlopszámokból adódik, és a szerkesztőben finomítható.
- A szimulált átlagos ciklusidő (mintegy 63 óra, azaz napi 15 munkaórával kb. 4,2 munkanap) megegyezik a folyamatáram-elemzés eredményével; az eloszlás azonban jobbra ferde: a határidő-egyeztetés és az utómunka miatt az esetek tizede jóval hosszabb ideig tart. A határidő vállalásakor ezért nem az átlaggal, hanem egy magasabb percentilissel érdemes számolni.
- A szimuláció nem modellezi az erőforrások versengését (a gép előtti sort az átlagos várakozás tartalmazza); ehhez sorbanállási modell vagy diszkrét eseményű szimuláció kell (kézikönyv 21. fejezet).
- Az eseménynapló a folyamatbányászati eszközlap gyakorló adata: a leggyakoribb út mellett az egyeztetéses és az utómunkás változatok is megjelennek.
"""),
]
