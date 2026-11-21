"""A ForgácsTech MES-ének eseménynaplója az első három hónapból (szimulált, determinisztikus).

Közös adat a folyamatbányászati sablonhoz és notebookhoz. A napló a valós (jelenlegi) működést
utánozza: a rendelések kb. 17%-át a termelésvezető átsorolja (a jövőbeli modellben ez a lépés nem
szerepel, kézikönyv 20. fejezet); az átsorolt rendelés a gép sorában előre kerül, de az anyagát csak a
következő műszak elején adják ki (kézikönyv 25. fejezet). Néhány rendelésnél utómunka kell, néhánynál
a mérés kimarad (megfelelőségi eltérés).

Időegység a szimulációban: munkanap (0,25 = 6:00, 0,583 = 14:00); a dátumok a hétvégéket kihagyják.
"""
import datetime as dt
import math
import random

GEPEK = ["E1", "E2", "E3", "MK1", "MK2", "MK3"]
MUSZAK = (0.25, 7 / 12)          # műszakkezdés: 6:00 és 14:00 (a napi anyagkiadás időpontjai)
KEZDO = dt.date(2026, 1, 5)       # hétfő
N_ESET = 300
IGERT_NAP = 10                    # vállalt átfutás munkanapban
P_ATSOROL, P_UTOMUNKA, P_MERES_KIMARAD = 0.17, 0.08, 0.03

MODELL_KOVETESEK = {               # a jövőbeli BPMN-modell szerint megengedett közvetlen követések
    ("Rendelés rögzítése", "Visszaigazolás"), ("Visszaigazolás", "Ütemezés"), ("Ütemezés", "Anyagkiadás"),
    ("Anyagkiadás", "Megmunkálás"), ("Megmunkálás", "Mérés"), ("Mérés", "Utómunka"), ("Utómunka", "Mérés"),
    ("Mérés", "Csomagolás"), ("Csomagolás", "Kiszállítás"),
}


def _kovetkezo_muszak(t):
    nap = math.floor(t)
    for m in MUSZAK:
        if nap + m >= t:
            return nap + m
    return nap + 1 + MUSZAK[0]


def _idobelyeg(t):
    """Munkanap-időből (float) dátum–idő a hétvégék kihagyásával."""
    nap = math.floor(t)
    het, mar = divmod(nap, 5)
    datum = KEZDO + dt.timedelta(days=7 * het + mar)
    perc = round((t - nap) * 24 * 60)
    return dt.datetime.combine(datum, dt.time()) + dt.timedelta(minutes=perc)


def szimulal():
    rnd = random.Random(20260121)
    esetek = []
    for i in range(N_ESET):
        t0 = rnd.uniform(0, 58) + 0.25
        t0 = math.floor(t0) + 0.25 + (t0 - math.floor(t0)) * 0.4      # munkaidőben érkezik
        esetek.append(dict(id=f"R{i + 1:04d}", t0=t0, gep=rnd.choice(GEPEK), sulyos=rnd.random() < P_ATSOROL,
                           megm=rnd.uniform(0.6, 1.55), utomunka=rnd.random() < P_UTOMUNKA,
                           meres_kimarad=rnd.random() < P_MERES_KIMARAD))
    esetek.sort(key=lambda e: e["t0"])
    for k, e in enumerate(esetek):
        e["id"] = f"R{k + 1:04d}"
    naplo = []

    def ev(e, nev, s, v, eroforras):
        naplo.append((e["id"], nev, s, v, eroforras))

    # ügyintézés az ütemezésig
    for e in esetek:
        t = e["t0"]; ev(e, "Rendelés rögzítése", t, t + 0.04, "értékesítés"); t += 0.04
        t += rnd.uniform(0.2, 0.9); ev(e, "Visszaigazolás", t, t + 0.04, "értékesítés"); t += 0.04
        t += rnd.uniform(0.1, 0.5); ev(e, "Ütemezés", t, t + 0.02, "termelésvezető"); t += 0.02
        e["utem"] = t
        if e["sulyos"]:
            ta = t + rnd.uniform(0.05, 0.6); ev(e, "Rendelés átsorolása", ta, ta + 0.01, "termelésvezető")
            e["prio"], e["anyag"] = ta, _kovetkezo_muszak(ta + 0.01)
        else:
            e["prio"], e["anyag"] = None, _kovetkezo_muszak(t)
        ev(e, "Anyagkiadás", e["anyag"], e["anyag"] + 0.03, "raktár")
        e["anyag"] += 0.03
    # gépenkénti sor: az átsorolt rendelés előre kerül, de az anyagára várni kell
    INDULO = {g: rnd.uniform(2.0, 4.0) for g in GEPEK}
    for g in GEPEK:
        sor = [e for e in esetek if e["gep"] == g]
        kesz, T = set(), INDULO[g]          # a gép a bevezetéskor még a korábbi rendeléseken dolgozik
        while len(kesz) < len(sor):
            jel = [e for e in sor if e["id"] not in kesz and e["utem"] <= T]
            if not jel:
                T = min(e["utem"] for e in sor if e["id"] not in kesz); continue
            atsorolt = [e for e in jel if e["prio"] is not None and e["prio"] <= T]
            e = min(atsorolt, key=lambda x: x["prio"]) if atsorolt else min(jel, key=lambda x: x["utem"])
            s = max(T, e["anyag"])
            e["varakozas_anyag"] = max(0.0, e["anyag"] - T)
            ev(e, "Megmunkálás", s, s + e["megm"], g)
            e["megm_vege"] = T = s + e["megm"]
            kesz.add(e["id"])
    # mérés, utómunka, csomagolás, kiszállítás
    for e in esetek:
        t = e["megm_vege"]
        if not e["meres_kimarad"]:
            t += rnd.uniform(0.05, 0.4); d = rnd.uniform(0.04, 0.12); ev(e, "Mérés", t, t + d, "minőségügy"); t += d
            if e["utomunka"]:
                t += rnd.uniform(0.1, 0.4); d = rnd.uniform(0.15, 0.4); ev(e, "Utómunka", t, t + d, e["gep"]); t += d
                t += rnd.uniform(0.05, 0.3); d = rnd.uniform(0.04, 0.1); ev(e, "Mérés", t, t + d, "minőségügy"); t += d
        t += rnd.uniform(0.1, 0.4); ev(e, "Csomagolás", t, t + 0.05, "expedíció"); t += 0.05
        t = _kovetkezo_muszak(t + 0.3); ev(e, "Kiszállítás", t, t + 0.02, "expedíció")
        e["vege"], e["hatarido"] = t + 0.02, math.floor(e["t0"]) + IGERT_NAP + 0.75
    naplo.sort(key=lambda r: (r[0], r[2]))
    esetlista = [(e["id"], _idobelyeg(e["t0"]), _idobelyeg(e["hatarido"]), e["gep"]) for e in esetek]
    sorok = [(a, b, _idobelyeg(c), _idobelyeg(d), f) for a, b, c, d, f in naplo]
    return esetlista, sorok


ESETEK, NAPLO = szimulal()

if __name__ == "__main__":
    import collections
    print(len(ESETEK), "eset,", len(NAPLO), "esemény")
    vege = collections.defaultdict(lambda: None)
    for a, b, c, d, f in NAPLO:
        if b == "Kiszállítás":
            vege[a] = d
    hatar = {a: h for a, _, h, _ in ESETEK}
    ido = sum(vege[a] <= hatar[a] for a in hatar) / len(hatar)
    atsor = {a for a, b, *_ in NAPLO if b == "Rendelés átsorolása"}
    print(f"határidőre: {ido:.1%}; átsorolt: {len(atsor) / len(hatar):.1%}")
