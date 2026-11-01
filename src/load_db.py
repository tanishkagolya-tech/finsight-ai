import sqlite3
import pandas as pd

conn = sqlite3.connect("data/finsight.db")

# 1. Crypto prices (BTC + ETH in one table)
frames = []
for symbol, name in [("BTC-USD", "btc"), ("ETH-USD", "eth")]:
    df = pd.read_csv(f"data/{name}.csv", parse_dates=["Date"])
    df["symbol"] = symbol
    frames.append(df)

prices = pd.concat(frames, ignore_index=True)
prices.columns = [c.lower() for c in prices.columns]
prices.to_sql("prices", conn, if_exists="replace", index=False)

# 2. Fraud transactions
tx = pd.read_csv("data/creditcard.csv")
tx.columns = [c.lower() for c in tx.columns]
tx.to_sql("transactions", conn, if_exists="replace", index=False)

# 3. Quick check
for table in ["prices", "transactions"]:
    n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(table, "rows:", n)

conn.close()
print("Database created: data/finsight.db")