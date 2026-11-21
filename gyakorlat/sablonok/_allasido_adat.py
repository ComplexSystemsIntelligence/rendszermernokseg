"""A ForgácsTech egy havi állásidő-naplója (közös adat a Pareto-sablonhoz és a notebookhoz).

Determinisztikusan előállított, a kézikönyv 25. fejezetének összegeivel egyező minta:
okonként a havi összes perc pontosan a fejezetben szereplő érték.
"""
import random

GEPEK = ["E1", "E2", "E3", "MK1", "MK2", "MK3"]
# ok: (havi összes perc, események száma, gépenkénti súlyok)
OKOK = {
    "anyagra várás": (1120, 38, [1, 1, 1, 3, 3, 3]),
    "átállás": (860, 22, [2, 2, 2, 1, 1, 1]),
    "szerszámcsere": (500, 25, [1, 1, 1, 2, 2, 2]),
    "programhiba": (340, 12, [0.5, 0.5, 0.5, 2, 2, 3]),
    "gépmeghibásodás": (300, 6, [3, 3, 1, 1, 1, 1]),
    "kezelőre várás": (230, 14, [1, 1, 1, 1, 1, 2]),
    "minőségellenőrzésre várás": (150, 10, [1, 1, 1, 1, 1, 1]),
    "egyéb": (100, 8, [1, 1, 1, 1, 1, 1]),
}
NAPOK = [d for d in range(2, 32) if (d - 2) % 7 not in (5, 6)]   # 2026. március munkanapjai (márc. 2. hétfő)


def naplo():
    rnd = random.Random(2026)
    sorok = []
    for ok, (ossz, db, suly) in OKOK.items():
        nyers = [rnd.lognormvariate(0, 0.6) for _ in range(db)]
        s = sum(nyers)
        percek = [max(3, round(v / s * ossz)) for v in nyers]
        percek[-1] += ossz - sum(percek)
        for p in percek:
            nap = rnd.choice(NAPOK)
            gep = rnd.choices(GEPEK, weights=suly)[0]
            sorok.append((f"2026-03-{nap:02d}", gep, ok, p))
    sorok.sort()
    return sorok


ADAT = naplo()

if __name__ == "__main__":
    from collections import Counter
    c = Counter()
    for _, _, ok, p in ADAT:
        c[ok] += p
    print(len(ADAT), dict(c), sum(c.values()))
