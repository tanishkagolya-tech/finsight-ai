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



\## Day 4



\- Fraud data has V1-V28 PCA features (anonymized): interpretable only through importance, not meaning.

\- Missing values: 0. Duplicate rows: 1,081 (1,062 normal, 19 fraud). Dropping them before splitting avoids train/test leakage; the fraud class shrinks from 492 to 473 (rate 0.167%).

\- Top features by absolute correlation with class: v17 (0.33), v14 (0.30), v12 (0.26). Fraud values sit far below 0 while normal values cluster tightly at 0.

\- Fraud amounts cluster at specific values (about $0, $1, $100) while normal amounts are smooth: possible card-testing behaviour (hypothesis, not proven).

\- Fraud rate by hour peaks at hours 2 (1.7%) and 4 (1.0%) versus 0.17% overall, but with only 473 frauds the pattern is noisy; 'time' is seconds from the first transaction, not clock time.

\- Only 473 frauds after dedup: a 20% test set has about 95 frauds, so metrics are noisy. Use stratified splits and cross-validation in Week 3.



\## Day 5



\- Week 1 SQL goal reached: 22 queries covering aggregation, window functions (LAG, running MAX, RANK), CTEs, JOINs and HAVING.

\- Computed daily returns and drawdown in SQL; will recompute in pandas in Week 2 to cross-check.

\- BTC max drawdown in this data: -76.6% (2022-11-21, close 15,787 vs peak 67,567). Top-5 drawdown rows are all from one episode.

\- 105 BTC days (about 4%) fell more than 5%. Big crashes are followed by big rebounds (March 2020, Nov 2022, Feb 2026): volatility clustering.

\- ETH is more volatile than BTC (best day +25.9% vs +18.8%); 3 of ETH's top-10 days are also BTC top-10 days; ETH rose while BTC fell on 236 days (about 9.5%).

\- Big-volume days match big price moves, except 2021-02-26 (volume 351B, price -1.6%): further evidence it is a data error. Its effect on the yearly mean is small (about 0.8B), but it matters for the max and for models.

\- BTC average volume is higher in bull years and lowest in 2023 (18.3B).

\- Fraud rate is U-shaped by amount (0.256% under 10, 0.061% for 10-50, 0.290% for 200+), peaks at hours 2 and 4, and is 1.48% for zero-amount transactions (8.6x the base rate).

\- v14 and v17 averages differ by about 7 units between fraud and normal: strong features for Week 3.

