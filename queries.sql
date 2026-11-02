-- Query 1: rows per symbol, with first and last date
SELECT symbol, COUNT(*) AS days, MIN(date) AS first_day, MAX(date) AS last_day
FROM prices
GROUP BY symbol;

-- Query 2: highest closing price for each symbol
SELECT symbol, MAX(close) AS highest_close
FROM prices
GROUP BY symbol;

-- Query 3: how many fraud (class = 1) vs normal (class = 0) transactions
SELECT class, COUNT(*) AS n
FROM transactions
GROUP BY class;

-- Query 4: average amount for fraud vs normal transactions
SELECT class, AVG(amount) AS avg_amount
FROM transactions
GROUP BY class;

-- Query 5: the 5 days with the highest BTC volume
SELECT date, volume
FROM prices
WHERE symbol = 'BTC-USD'
ORDER BY volume DESC
LIMIT 5;

-- Query 6: yesterday's close next to today's (LAG basics)
SELECT date, close, LAG(close) OVER (ORDER BY date) AS prev_close
FROM prices
WHERE symbol = 'BTC-USD'
ORDER BY date
LIMIT 10;

-- Query 7: 7-day moving average of BTC close (latest 10 days)
SELECT date, close,
       ROUND(AVG(close) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 0) AS ma7
FROM prices
WHERE symbol = 'BTC-USD'
ORDER BY date DESC
LIMIT 10;

-- Query 8: yearly average, high and low close per symbol
SELECT symbol, strftime('%Y', date) AS year,
       ROUND(AVG(close), 0) AS avg_close, MAX(close) AS max_close, MIN(close) AS min_close
FROM prices
GROUP BY symbol, year
ORDER BY symbol, year;

-- Query 9: 10 best BTC days (daily % return)
WITH r AS (
  SELECT date, close / LAG(close) OVER (ORDER BY date) - 1 AS ret
  FROM prices WHERE symbol = 'BTC-USD'
)
SELECT date, ROUND(ret * 100, 2) AS pct_return
FROM r
WHERE ret IS NOT NULL
ORDER BY ret DESC
LIMIT 10;

-- Query 10: 10 worst BTC days (daily % return)
WITH r AS (
  SELECT date, close / LAG(close) OVER (ORDER BY date) - 1 AS ret
  FROM prices WHERE symbol = 'BTC-USD'
)
SELECT date, ROUND(ret * 100, 2) AS pct_return
FROM r
WHERE ret IS NOT NULL
ORDER BY ret ASC
LIMIT 10;

-- Query 11: how many BTC days fell more than 5%
WITH r AS (
  SELECT date, close / LAG(close) OVER (ORDER BY date) - 1 AS ret
  FROM prices WHERE symbol = 'BTC-USD'
)
SELECT COUNT(*) AS days_down_over_5pct
FROM r
WHERE ret < -0.05;

-- Query 12: BTC and ETH side by side (JOIN), latest 10 days
SELECT b.date, b.close AS btc_close, e.close AS eth_close,
       ROUND(b.close / e.close, 1) AS btc_per_eth
FROM prices b
JOIN prices e ON b.date = e.date AND e.symbol = 'ETH-USD'
WHERE b.symbol = 'BTC-USD'
ORDER BY b.date DESC
LIMIT 10;

-- Query 13: days when ETH rose but BTC fell
WITH r AS (
  SELECT symbol, date,
         close / LAG(close) OVER (PARTITION BY symbol ORDER BY date) - 1 AS ret
  FROM prices
)
SELECT COUNT(*) AS eth_up_btc_down_days
FROM r b
JOIN r e ON b.date = e.date
WHERE b.symbol = 'BTC-USD' AND e.symbol = 'ETH-USD'
  AND e.ret > 0 AND b.ret < 0;

-- Query 14: top 3 BTC volume days in each year (RANK per year)
WITH x AS (
  SELECT strftime('%Y', date) AS year, date, volume,
         RANK() OVER (PARTITION BY strftime('%Y', date) ORDER BY volume DESC) AS rk
  FROM prices WHERE symbol = 'BTC-USD'
)
SELECT year, date, volume, rk
FROM x
WHERE rk <= 3
ORDER BY year, rk;

-- Query 15: 5 deepest BTC drawdowns (distance below the running peak)
WITH x AS (
  SELECT date, close, MAX(close) OVER (ORDER BY date) AS peak
  FROM prices WHERE symbol = 'BTC-USD'
)
SELECT date, close, peak, ROUND((close / peak - 1) * 100, 1) AS drawdown_pct
FROM x
ORDER BY drawdown_pct ASC
LIMIT 5;

-- Query 16: fraud rate by transaction amount bucket
SELECT CASE WHEN amount < 10 THEN '1: under 10'
            WHEN amount < 50 THEN '2: 10-50'
            WHEN amount < 200 THEN '3: 50-200'
            ELSE '4: 200+' END AS bucket,
       COUNT(*) AS n, SUM(class) AS frauds,
       ROUND(100.0 * SUM(class) / COUNT(*), 3) AS fraud_pct
FROM transactions
GROUP BY bucket
ORDER BY bucket;

-- Query 17: fraud rate by hour
SELECT CAST(time / 3600 AS INTEGER) % 24 AS hour,
       COUNT(*) AS n, SUM(class) AS frauds,
       ROUND(100.0 * SUM(class) / COUNT(*), 3) AS fraud_pct
FROM transactions
GROUP BY hour
ORDER BY hour;

-- Query 18: only the hours where fraud is above 0.5% (HAVING)
SELECT CAST(time / 3600 AS INTEGER) % 24 AS hour,
       COUNT(*) AS n, SUM(class) AS frauds,
       ROUND(100.0 * SUM(class) / COUNT(*), 3) AS fraud_pct
FROM transactions
GROUP BY hour
HAVING 1.0 * SUM(class) / COUNT(*) > 0.005
ORDER BY fraud_pct DESC;

-- Query 19: average v14 and v17 by class
SELECT class, ROUND(AVG(v14), 2) AS avg_v14, ROUND(AVG(v17), 2) AS avg_v17
FROM transactions
GROUP BY class;

-- Query 20: transactions with amount exactly 0, by class
SELECT class, COUNT(*) AS n
FROM transactions
WHERE amount = 0
GROUP BY class;

-- Query 21: 10 best ETH days (daily % return)
WITH r AS (
  SELECT date, close / LAG(close) OVER (ORDER BY date) - 1 AS ret
  FROM prices WHERE symbol = 'ETH-USD'
)
SELECT date, ROUND(ret * 100, 2) AS pct_return
FROM r
WHERE ret IS NOT NULL
ORDER BY ret DESC
LIMIT 10;

-- Query 22: BTC average daily volume per year (in billions)
SELECT strftime('%Y', date) AS year,
       ROUND(AVG(volume) / 1e9, 1) AS avg_volume_billion
FROM prices
WHERE symbol = 'BTC-USD'
GROUP BY year
ORDER BY year;