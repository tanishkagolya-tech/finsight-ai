import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("data/finsight.db")
tx = pd.read_sql("SELECT * FROM transactions", conn)
conn.close()

# 1. Basic health checks
print("Shape:", tx.shape)
print("Missing values:", tx.isna().sum().sum())
print("Duplicate rows:", tx.duplicated().sum())
print(tx["class"].value_counts(normalize=True), "\n")

# 2. Which features separate fraud from normal?
features = [c for c in tx.columns if c.startswith("v")]
corr = tx.corr()["class"].drop("class").abs().sort_values(ascending=False)
print("Top 10 features by |correlation| with class:")
print(corr.head(10), "\n")

# 3. Fraud rate by hour (hours since first transaction, mod 24)
tx["hour"] = (tx["time"] // 3600) % 24
rate = tx.groupby("hour")["class"].mean()
print("Fraud rate by hour:")
print(rate.round(5), "\n")

# 4. Charts
top = list(corr.index[:2])
fig, ax = plt.subplots(2, 2, figsize=(12, 9))

rate.plot(kind="bar", ax=ax[0, 0])
ax[0, 0].set_title("Fraud rate by hour")

for c, label in [(0, "normal"), (1, "fraud")]:
    ax[0, 1].hist(np.log1p(tx.loc[tx["class"] == c, "amount"]),
                  bins=50, density=True, alpha=0.5, label=label)
ax[0, 1].set_title("log(1 + amount) by class")
ax[0, 1].legend()

for i, f in enumerate(top):
    for c, label in [(0, "normal"), (1, "fraud")]:
        ax[1, i].hist(tx.loc[tx["class"] == c, f],
                      bins=50, density=True, alpha=0.5, label=label)
    ax[1, i].set_title(f"{f}: fraud vs normal")
    ax[1, i].legend()

plt.tight_layout()
plt.savefig("reports/fraud_eda_day4.png", dpi=120)
print("Saved reports/fraud_eda_day4.png")