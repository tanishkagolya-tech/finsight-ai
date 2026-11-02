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



\- Use log returns instead of raw prices: they add up across days and are easier to compare over time.

\- Dropped the last (incomplete) day before computing returns.

\- BTC returns show fat tails (high excess kurtosis): a normal-distribution risk model would underestimate extreme days.

\- BTC volatility clusters: calm and wild periods come in groups. This is why Week 5 forecasts volatility, not price.

\- 2021-02-26 BTC volume (351B) is about 3x the next-largest nearby day while price barely moved: likely a data error. Flagged, not deleted. Verify against another source.

\- Compare medians as well as means: fraud median ($9.25) is far below normal median ($22.00) even though the fraud mean is higher ($122 vs $88). Amounts are right-skewed, so amount alone cannot detect fraud.

\- BTC daily log returns (2020-2026, 2,495 days): mean 0.095%, std 3.14% (about 60% annualized), skew -1.30, excess kurtosis 22.3.

\- Worst day 2020-03-12 (log return -0.46, about -37%) is roughly 15 standard deviations below the mean: practically impossible under a normal model.

\- Best day 2021-02-08 (log return +0.17, about +19%).

