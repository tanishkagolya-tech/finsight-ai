import sqlite3
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold

conn = sqlite3.connect("data/finsight.db")
tx = pd.read_sql("SELECT * FROM transactions", conn)

# 1. Duplicates split se PEHLE hatao
print("Raw rows:", len(tx))
tx = tx.drop_duplicates().reset_index(drop=True)
print("After dedup:", len(tx), "| frauds:", int(tx["class"].sum()))

X = tx.drop(columns=["class"])
y = tx["class"]

# 2. Dikhao ki stratify kyun zaroori hai: bina stratify, test mein frauds ki ginti badalti rehti hai
print("\nWithout stratify, frauds in test set for 5 different seeds:")
for seed in range(5):
    _, yt = train_test_split(y, test_size=0.2, random_state=seed)
    print("  seed", seed, "->", int(yt.sum()))

# 3. Asli split: stratified, seed fix
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
print("\nWith stratify (seed 42):")
print("Train:", len(X_train), "rows,", int(y_train.sum()), "frauds,",
      round(100 * y_train.mean(), 3), "%")
print("Test: ", len(X_test), "rows,", int(y_test.sum()), "frauds,",
      round(100 * y_test.mean(), 3), "%")

# 4. Overlap check
print("Duplicate feature rows across train+test:",
      int(pd.concat([X_train, X_test]).duplicated().sum()))

# 5. 5-fold cross-validation sirf TRAIN par
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
print("\nCV folds inside train:")
for i, (tr, va) in enumerate(skf.split(X_train, y_train)):
    print("  fold", i, "| train rows", len(tr), "| validation frauds", int(y_train.iloc[va].sum()))

# 6. Time check (sirf jaankari ke liye): kya last 20% time mein frauds hain?
cut = tx["time"].quantile(0.8)
print("\nFrauds in first 80% of time:", int(tx.loc[tx["time"] <= cut, "class"].sum()),
      "| in last 20%:", int(tx.loc[tx["time"] > cut, "class"].sum()))

# 7. Split ko database mein save karo taaki Week 3 mein wahi split use ho
tx["split"] = "train"
tx.loc[X_test.index, "split"] = "test"
tx.to_sql("transactions_split", conn, if_exists="replace", index=False)
conn.close()
print("\nSaved table transactions_split with a 'split' column")