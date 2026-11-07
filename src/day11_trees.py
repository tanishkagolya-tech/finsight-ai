import sqlite3
import time
import warnings
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

# Sirf TRAIN rows. Test set ko haath nahi lagana.
conn = sqlite3.connect("data/finsight.db")
df = pd.read_sql("SELECT * FROM transactions_split WHERE split = 'train'", conn)
conn.close()

y = df["class"]
X = df.drop(columns=["class", "split", "time"])
spw = (len(y) - y.sum()) / y.sum()  # normal : fraud ratio
print("Train rows:", len(y), "| frauds:", int(y.sum()), "| scale_pos_weight:", round(spw))

xgb_params = dict(n_estimators=300, max_depth=4, learning_rate=0.1, subsample=0.8,
                  colsample_bytree=0.8, tree_method="hist", n_jobs=-1, random_state=42)

models = {
    "LogReg": Pipeline([("scale", StandardScaler()),
                        ("lr", LogisticRegression(max_iter=1000))]),
    "RandomForest": RandomForestClassifier(n_estimators=100, min_samples_leaf=2,
                                           n_jobs=-1, random_state=42),
    "XGBoost": XGBClassifier(**xgb_params),
    "XGBoost + spw": XGBClassifier(scale_pos_weight=spw, **xgb_params),
}

# Wahi 5 folds jo Day 9 aur 10 mein the
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scoring = {"pr_auc": "average_precision", "roc_auc": "roc_auc"}

summary, per_fold = [], {}
for name, model in models.items():
    print("Running:", name, "...", flush=True)
    t0 = time.time()
    r = cross_validate(model, X, y, cv=skf, scoring=scoring, n_jobs=1)
    per_fold[name] = r["test_pr_auc"]
    summary.append({
        "model": name,
        "pr_auc": f"{r['test_pr_auc'].mean():.3f} +/- {r['test_pr_auc'].std():.3f}",
        "roc_auc": f"{r['test_roc_auc'].mean():.3f} +/- {r['test_roc_auc'].std():.3f}",
        "sec_per_fold": round(r["fit_time"].mean(), 1),
        "total_min": round((time.time() - t0) / 60, 1),
    })

res = pd.DataFrame(summary).set_index("model")
print("\n", res.to_string())
res.to_csv("reports/day11_models.csv")

# Fold-by-fold PR-AUC: kya fark har fold mein dikhta hai?
pf = pd.DataFrame(per_fold).round(3)
pf.index = [f"fold {i}" for i in range(5)]
print("\nPR-AUC per fold:\n", pf.to_string())

print("\nPaired difference vs LogReg (same folds):")
for name in pf.columns[1:]:
    d = pf[name] - pf["LogReg"]
    print(f"  {name:15s} mean diff {d.mean():+.3f} | better in {int((d > 0).sum())} of 5 folds")

# XGBoost kin features par bharosa karta hai (train par fit, test nahi dekha)
xgb = XGBClassifier(**xgb_params).fit(X, y)
imp = pd.Series(xgb.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\nXGBoost top 10 features (gain importance, normalized):")
print(imp.head(10).round(3).to_string())