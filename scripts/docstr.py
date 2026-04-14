import random
import pandas as pd

seed = 741
n = 3

rng = random.Random(seed)

cls = pd.DataFrame

atts = pd.Series(
    {k: type(getattr(cls, k)).__name__ for k in dir(cls) if not k.startswith("_")}
)

print(atts.value_counts())


for idx, v in atts.sample(n, random_state=seed).items():
    print(idx, v)
    print(getattr(cls, str(idx)).__doc__)
