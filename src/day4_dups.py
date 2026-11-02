import sqlite3
import pandas as pd

conn = sqlite3.connect("data/finsight.db")
tx = pd.read_sql("SELECT * FROM transactions", conn)
conn.close()

dup = tx.duplicated()
print("Duplicates by class:")
print(tx[dup]["class"].value_counts(), "\n")
print("Class counts after dropping duplicates:")
print(tx.drop_duplicates()["class"].value_counts())