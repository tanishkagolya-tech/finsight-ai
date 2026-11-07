import sqlite3
import warnings
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import make_scorer, precision_score, recall_score

warnings.filterwarnings("ignore")

# Sirf TRAIN rows. Test set ko haath nahi lagana.
conn = sqlite3.connect("data/finsight.db")
df = pd.read_sql("SELECT * FROM transactions_split WHERE split = 'train'", conn)
conn.close()

y = df["class"]
X = df.drop(columns=["class", "split", "time"])  # 'time' = 2-din ke window mein position, asli feature nahi
print("Train rows:", len(X), "| frauds:", int(y.sum()), "| features:", X.shape[1])

scoring = {
    "accuracy": "accuracy",
    "precision": make_scorer(precision_score, zero_division=0),
    "recall": make_scorer(recall_score, zero_division=0),
    "pr_auc": "average_precision",
    "roc_auc": "roc_auc",
}

models = {
    "Dummy (prior)": DummyClassifier(strategy="prior"),
    "LogReg": Pipeline([("scale", StandardScaler()),
                        ("lr", LogisticRegression(max_iter=1000))]),
    "LogReg balanced": Pipeline([("scale", StandardScaler()),
                                 ("lr", LogisticRegression(max_iter=1000, class_weight="balanced"))]),
}

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

rows = []
for name, model in models.items():
    print("Running:", name, "...")
    r = cross_validate(model, X, y, cv=skf, scoring=scoring, n_jobs=1)
    row = {"model": name}
    for k in scoring:
        v = r[f"test_{k}"]
        row[k] = f"{v.mean():.3f} +/- {v.std():.3f}"
    rows.append(row)

res = pd.DataFrame(rows).set_index("model")
print()
print(res.to_string())
res.to_csv("reports/day9_baselines.csv")
print("\nSaved reports/day9_baselines.csv")