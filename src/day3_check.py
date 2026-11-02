import sqlite3
import pandas as pd

conn = sqlite3.connect("data/finsight.db")
df = pd.read_sql(
    "SELECT date, close, volume FROM prices "
    "WHERE symbol = 'BTC-USD' AND date BETWEEN '2021-02-20' AND '2021-03-05'",
    conn,
)
print(df)