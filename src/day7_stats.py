import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

conn = sqlite3.connect("data/finsight.db")
prices = pd.read_sql("SELECT * FROM prices", conn, parse_dates=["date"])
tx = pd.read_sql("SELECT * FROM transactions", conn)
conn.close()


def close(sym):
    d = prices[prices["symbol"] == sym].set_index("date").sort_index()["close"]
    return d.iloc[:-1]  # drop today's incomplete row


def fmt(p):
    return "< 0.0001" if p < 0.0001 else f"{p:.4f}"


btc_log, eth_log = np.log(close("BTC-USD")), np.log(close("ETH-USD"))
ret = pd.DataFrame({"btc": btc_log.diff(), "eth": eth_log.diff()}).dropna()

# ---------- Part 1: BTC vs ETH correlation ----------
print("PART 1: BTC vs ETH correlation")
print("Correlation of log PRICES (misleading):", round(btc_log.corr(eth_log), 3))
print("Pearson on returns: ", round(ret["btc"].corr(ret["eth"]), 3))
print("Spearman on returns:", round(ret["btc"].corr(ret["eth"], method="spearman"), 3))

rng = np.random.default_rng(42)
x, y, n = ret["btc"].values, ret["eth"].values, len(ret)
boot = []
for _ in range(2000):
    i = rng.integers(0, n, n)
    boot.append(np.corrcoef(x[i], y[i])[0, 1])
lo, hi = np.percentile(boot, [2.5, 97.5])
print(f"Bootstrap 95% interval for Pearson: [{lo:.3f}, {hi:.3f}]")

roll = ret["btc"].rolling(90).corr(ret["eth"])
print("Rolling 90-day correlation: min", round(roll.min(), 2), "max", round(roll.max(), 2))
plt.figure(figsize=(10, 4))
roll.plot()
plt.title("BTC-ETH rolling 90-day correlation of daily returns")
plt.tight_layout()
plt.savefig("reports/btc_eth_corr_day7.png", dpi=120)
plt.close()

# ---------- Part 2: is ETH more volatile than BTC? ----------
print("\nPART 2: ETH vs BTC volatility")
print("Std of daily returns: BTC", round(ret["btc"].std(), 4), "| ETH", round(ret["eth"].std(), 4),
      "| ratio", round(ret["eth"].std() / ret["btc"].std(), 2))
diff = ret["eth"].abs() - ret["btc"].abs()
w = stats.wilcoxon(diff)
print("Share of days where ETH moved more than BTC:", round((diff > 0).mean(), 3))
print("Wilcoxon signed-rank on |ETH| - |BTC|: p =", fmt(w.pvalue))

# ---------- Part 3: fraud vs normal ----------
print("\nPART 3: fraud vs normal (duplicates removed)")
tx = tx.drop_duplicates()
fraud, normal = tx[tx["class"] == 1], tx[tx["class"] == 0]
print("Fraud rows:", len(fraud), "| Normal rows:", len(normal))
for col in ["amount", "v14", "v17"]:
    u = stats.mannwhitneyu(fraud[col], normal[col], alternative="two-sided")
    cles = u.statistic / (len(fraud) * len(normal))
    print(f"{col:6s} median fraud {fraud[col].median():8.2f} | median normal {normal[col].median():8.2f} "
          f"| p = {fmt(u.pvalue)} | P(fraud value > normal value) = {cles:.3f}")