import sqlite3
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import precision_recall_curve, average_precision_score

warnings.filterwarnings("ignore")

# Sirf TRAIN rows. Test set ko haath nahi lagana.
conn = sqlite3.connect("data/finsight.db")
df = pd.read_sql("SELECT * FROM transactions_split WHERE split = 'train'", conn)
conn.close()

y = df["class"].values
X = df.drop(columns=["class", "split", "time"])
n_fraud, n_normal = int(y.sum()), int((y == 0).sum())
print("Train rows:", len(y), "| frauds:", n_fraud)


def make(cw=None):
    return Pipeline([("scale", StandardScaler()),
                     ("lr", LogisticRegression(max_iter=1000, class_weight=cw))])


skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
p_plain = cross_val_predict(make(), X, y, cv=skf, method="predict_proba")[:, 1]
p_bal = cross_val_predict(make("balanced"), X, y, cv=skf, method="predict_proba")[:, 1]

print("\nPooled out-of-fold PR-AUC  plain:", round(average_precision_score(y, p_plain), 3),
      "| balanced:", round(average_precision_score(y, p_bal), 3))

# Har threshold par tp / fp / fn (plain model)
ts = np.linspace(0.001, 0.999, 999)


def counts(p):
    out = []
    for t in ts:
        pred = p >= t
        tp = int((pred & (y == 1)).sum())
        fp = int((pred & (y == 0)).sum())
        out.append((tp, fp, n_fraud - tp))
    return np.array(out)


C = counts(p_plain)
tp, fp, fn = C[:, 0], C[:, 1], C[:, 2]

# ---------- Part 1: kya class_weight sirf threshold khiskata hai? ----------
pred_b = p_bal >= 0.5
tp_b = int((pred_b & (y == 1)).sum())
fp_b = int((pred_b & (y == 0)).sum())
rec_b, prec_b = tp_b / n_fraud, tp_b / max(tp_b + fp_b, 1)
print(f"\nPART 1: balanced @0.5 -> recall {rec_b:.3f}, precision {prec_b:.3f}, "
      f"frauds caught {tp_b}, false alarms {fp_b}")
ok = np.where(tp / n_fraud >= rec_b)[0]
i = ok[-1]  # sabse sakht threshold jo wahi recall deta hai
print(f"Plain model @ threshold {ts[i]:.3f} -> recall {tp[i] / n_fraud:.3f}, "
      f"precision {tp[i] / max(tp[i] + fp[i], 1):.3f}, "
      f"frauds caught {tp[i]}, false alarms {fp[i]}")

# ---------- Part 2: cost-based threshold ----------
print("\nPART 2: cost = ratio * missed_frauds + false_alarms   (plain model, OOF)")
print("ratio | best threshold | frauds caught | false alarms | missed | cost | flag-nothing cost | flag-everything cost")
best_for_plot = None
for ratio in [10, 100, 500]:
    cost = ratio * fn + fp
    j = int(np.argmin(cost))
    print(f"{ratio:5d} | {ts[j]:14.3f} | {tp[j]:13d} | {fp[j]:12d} | {fn[j]:6d} | "
          f"{cost[j]:5d} | {ratio * n_fraud:17d} | {n_normal:20d}")
    if ratio == 100:
        best_for_plot = (j, cost)

# ---------- Chart ----------
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
for name, p in [("LogReg", p_plain), ("LogReg balanced", p_bal)]:
    pr, rc, _ = precision_recall_curve(y, p)
    ax[0].plot(rc, pr, label=name)
ax[0].axhline(n_fraud / len(y), color="grey", linestyle="--", label="random (fraud rate)")
ax[0].set_xlabel("recall")
ax[0].set_ylabel("precision")
ax[0].set_title("Precision-recall curve (out-of-fold)")
ax[0].legend()

j, cost = best_for_plot
ax[1].plot(ts, cost)
ax[1].axvline(ts[j], color="red", linestyle="--", label=f"best threshold {ts[j]:.2f}")
ax[1].set_yscale("log")
ax[1].set_xlabel("threshold")
ax[1].set_ylabel("total cost (log scale)")
ax[1].set_title("Cost vs threshold (1 missed fraud = 100 false alarms)")
ax[1].legend()
plt.tight_layout()
plt.savefig("reports/day10_threshold.png", dpi=120)
print("\nSaved reports/day10_threshold.png")