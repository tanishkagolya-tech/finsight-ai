import sqlite3
import pandas as pd

conn = sqlite3.connect("data/finsight.db")

query = """
SELECT symbol, MAX(close) AS highest_close
FROM prices
GROUP BY symbol
"""
print(pd.read_sql(query, conn))