"""KoboCella beérkező csavartételek csavarozási próbája (közös adat a hisztogram-sablonhoz és -notebookhoz).

Két tétel (A: korábbi beszállítói gyártóhely, B: új gyártóhely), tételenként 60 kötés.
X: a bitbetéttel addig végzett csavarozások száma [ezer]; Y: a mért nyomaték [Nm].
A kétlépcsős csavarozási stratégiánál a kopás hatása kicsi (kb. −0,0014 Nm/ezer csavarozás, kézikönyv 18. fejezet).
"""
import random

TURES = (3.8, 4.2)


def adat():
    rnd = random.Random(42)
    sorok = []
    for tetel, kozep in (("A tétel", 4.020), ("B tétel", 3.950)):
        for _ in range(60):
            x = round(rnd.uniform(0, 20), 1)
            y = round(kozep - 0.0014 * x + rnd.gauss(0, 0.040), 3)
            sorok.append((tetel, x, y))
    return [(i + 1, t, x, y) for i, (t, x, y) in enumerate(sorok)]


ADAT = adat()

if __name__ == "__main__":
    import statistics as st
    for t in ("A tétel", "B tétel"):
        y = [r[3] for r in ADAT if r[1] == t]
        print(t, round(st.mean(y), 4), round(st.stdev(y), 4), min(y), max(y))
    y = [r[3] for r in ADAT]; print("össz", round(st.mean(y), 4), round(st.stdev(y), 4))
