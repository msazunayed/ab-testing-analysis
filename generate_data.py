import os
import numpy as np
import pandas as pd

np.random.seed(42)  # keeping this fixed so results are reproducible
os.makedirs("data", exist_ok=True)

N_DAYS = 14
USERS_PER_DAY = 3000
START_DATE = pd.Timestamp("2026-06-01")

rows = []
user_id = 100000

for day in range(N_DAYS):
    date = START_DATE + pd.Timedelta(days=day)
    for _ in range(USERS_PER_DAY):
        user_id += 1
        group = np.random.choice(["control", "treatment"], p=[0.5, 0.5])
        device = np.random.choice(["mobile", "desktop"], p=[0.64, 0.36])

        # desktop users just convert a little better than mobile regardless of the test
        base_rate = 0.100 if device == "mobile" else 0.115

        if group == "control":
            p = base_rate
        else:
            # this is the part that makes the story interesting - mobile actually
            # responds to the new button, desktop basically doesn't
            true_lift = 0.028 if device == "mobile" else 0.001

            # and here's a novelty bump for the first few days that goes away later,
            # since that happens a lot in real tests and it's worth having in the data
            novelty_bonus = 0.03 if day < 3 else 0.0
            p = base_rate + true_lift + novelty_bonus

        converted = np.random.binomial(1, p)

        # only converted users spend money, and spend is skewed not normal
        if converted:
            mu = 3.75 if group == "control" else 3.80  # treatment users spend slightly more on average
            revenue = float(np.round(np.random.lognormal(mean=mu, sigma=0.45), 2))
        else:
            revenue = 0.0

        rows.append([user_id, date, group, device, converted, revenue])

df = pd.DataFrame(rows, columns=["user_id", "date", "group", "device", "converted", "revenue"])
df = df.sample(frac=1, random_state=1).reset_index(drop=True)  # shuffle so it doesn't look neatly ordered by day

df.to_csv("data/ab_test_data.csv", index=False)

# quick sanity print so I can eyeball it before moving to the notebook
print(df.shape)
print(df.head())
print(df.groupby("group")["converted"].mean())
