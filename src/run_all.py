import sqlite3
import pandas as pd

conn = sqlite3.connect("data/finsight.db")
sql = open("queries.sql").read()

for q in sql.split(";"):
    if q.strip():
        print(q.strip().splitlines()[0])  # prints the comment line
        print(pd.read_sql(q, conn), "\n")