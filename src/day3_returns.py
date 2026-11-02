import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load BTC from the SQLite database
conn = sqlite3.connect("data/finsight.db")
prices = pd.read_sql("SELECT * FROM prices", conn, parse_dates=["date"])
conn.close()

btc = prices[prices["symbol"] == "BTC-USD"].set_index("date").sort_index()
btc = btc.iloc[:-1]  # drop today's incomplete row

# Returns and volatility
btc["return"] = btc["close"].pct_change()
btc["log_return"] = np.log(btc["close"] / btc["close"].shift(1))
btc["vol_30d"] = btc["log_return"].rolling(30).std()

r = btc["log_return"].dropna()
print("Days:", len(r))
print("Mean daily log return:", round(r.mean(), 5))
print("Daily volatility (std):", round(r.std(), 5))
print("Skew:", round(r.skew(), 3))
print("Excess kurtosis:", round(r.kurtosis(), 3))
print("Best day:", r.idxmax().date(), round(r.max(), 4))
print("Worst day:", r.idxmin().date(), round(r.min(), 4))

# Charts
fig, ax = plt.subplots(3, 1, figsize=(10, 11))

ax[0].plot(btc.index, btc["close"])
ax[0].set_yscale("log")
ax[0].set_title("BTC close price (log scale)")

ax[1].hist(r, bins=80, density=True, alpha=0.7, label="BTC log returns")
x = np.linspace(r.min(), r.max(), 300)
normal = np.exp(-((x - r.mean()) ** 2) / (2 * r.std() ** 2)) / (r.std() * np.sqrt(2 * np.pi))
ax[1].plot(x, normal, color="red", label="Normal curve")
ax[1].set_title("Return distribution vs normal curve")
ax[1].legend()

ax[2].plot(btc.index, btc["vol_30d"])
ax[2].set_title("30-day rolling volatility")

plt.tight_layout()
plt.savefig("reports/btc_day3.png", dpi=120)
print("Saved reports/btc_day3.png")