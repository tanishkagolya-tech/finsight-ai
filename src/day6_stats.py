import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.tsa.stattools import adfuller, acf

conn = sqlite3.connect("data/finsight.db")
prices = pd.read_sql("SELECT * FROM prices", conn, parse_dates=["date"])
conn.close()


def get_close(symbol):
    d = prices[prices["symbol"] == symbol].set_index("date").sort_index()
    return d["close"].iloc[:-1]  # drop today's incomplete row


def fmt(p):
    return "< 0.0001" if p < 0.0001 else f"{p:.4f}"


for symbol in ["BTC-USD", "ETH-USD"]:
    close = get_close(symbol)
    log_price = np.log(close)
    ret = log_price.diff().dropna()

    print("=" * 55)
    print(symbol, "| days:", len(ret))

    # 1. Stationarity (ADF)
    for name, series in [("log price", log_price), ("log return", ret)]:
        stat, p = adfuller(series, autolag="AIC")[:2]
        verdict = "stationary" if p < 0.05 else "NOT stationary"
        print(f"ADF {name:10s}: stat={stat:8.3f}  p={fmt(p)}  -> {verdict}")

    # 2. Normality (Jarque-Bera), plus a simulated normal series as a sanity check
    jb = stats.jarque_bera(ret)
    print(f"Jarque-Bera on returns:         stat={jb.statistic:.1f}  p={fmt(jb.pvalue)}")
    fake = np.random.default_rng(42).normal(ret.mean(), ret.std(), len(ret))
    jb_fake = stats.jarque_bera(fake)
    print(f"Jarque-Bera on simulated normal: stat={jb_fake.statistic:.1f}  p={fmt(jb_fake.pvalue)}")
    print("Skew:", round(ret.skew(), 3), "| Excess kurtosis:", round(ret.kurtosis(), 3))

    # 3. Autocorrelation of returns vs squared returns
    band = 1.96 / np.sqrt(len(ret))
    a_ret = acf(ret, nlags=10)[1:]
    a_sq = acf(ret ** 2, nlags=10)[1:]
    print(f"95% band: +/-{band:.3f}")
    print("ACF of returns, lags 1-10:        ", np.round(a_ret, 3))
    print("ACF of squared returns, lags 1-10:", np.round(a_sq, 3))

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for axis, vals, title in [(ax[0], a_ret, "ACF of returns"),
                              (ax[1], a_sq, "ACF of squared returns")]:
        axis.bar(range(1, 11), vals)
        axis.axhline(band, color="red", linestyle="--")
        axis.axhline(-band, color="red", linestyle="--")
        axis.set_title(f"{symbol}: {title}")
        axis.set_xlabel("lag (days)")
    plt.tight_layout()
    out = f"reports/{symbol[:3].lower()}_day6_acf.png"
    plt.savefig(out, dpi=120)
    plt.close()
    print("Saved", out)