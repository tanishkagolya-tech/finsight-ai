import sqlite3
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf

conn = sqlite3.connect("data/finsight.db")
d = pd.read_sql("SELECT date, close FROM prices WHERE symbol='BTC-USD' ORDER BY date",
                conn, parse_dates=["date"]).set_index("date")["close"].iloc[:-1]
conn.close()

ret = np.log(d).diff().dropna()
band = 1.96 / np.sqrt(len(ret))
print("band:", round(band, 3))
print("ACF of |returns|:               ", np.round(acf(ret.abs(), nlags=10)[1:], 3))
ex = ret[~((ret.index >= "2020-03-01") & (ret.index <= "2020-03-31"))]
print("ACF of squared, March 2020 removed:", np.round(acf(ex ** 2, nlags=10)[1:], 3))