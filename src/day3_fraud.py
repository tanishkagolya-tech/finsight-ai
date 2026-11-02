import sqlite3
import pandas as pd

conn = sqlite3.connect("data/finsight.db")
tx = pd.read_sql("SELECT class, amount FROM transactions", conn)
conn.close()

print(tx.groupby("class")["amount"].agg(["count", "mean", "median", "max"]))