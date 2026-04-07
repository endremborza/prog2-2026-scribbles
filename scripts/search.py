from random import Random
import time

rng = Random(742)

gen_digits = 20
div_digits = 9

upper = int(10**gen_digits)
diver = int(10**div_digits)

found = []

started = time.time()
while True:
    n = rng.randint(0, upper) % diver
    if n in found:
        break
    found.append(n)

print(
    f"found {n}, the {len(found)}th generation in {int((time.time() - started) * 1000)}ms"
)
