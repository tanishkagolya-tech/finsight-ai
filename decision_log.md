\# Decision Log



\## Day 1



\- Python 3.12 chosen over 3.13: ML libraries (SHAP, hmmlearn, torch) support lags behind the newest Python release.

\- Virtual environment (.venv): isolates dependencies so the project is reproducible.

\- data/ is in .gitignore: raw data is large and can be re-downloaded with yfinance.



\## Day 2



\- SQLite chosen over PostgreSQL: zero setup, single file, enough for this data size. Can migrate later.

\- Lowercased all column names so SQL queries stay consistent.

\- Fraud data is \~0.17% positive: accuracy will be a misleading metric. Will use PR-AUC.

\- Last row of price data is the current, incomplete day: drop it before modeling.



\## Day 3



\- Use log returns instead of raw prices: stationary-ish, additive over time.

\- Dropped the last (incomplete) day before computing returns.

\- BTC returns show fat tails (high excess kurtosis): a normal-distribution risk model would underestimate extreme days.

\- Compare medians as well as means: fraud amounts are skewed.

