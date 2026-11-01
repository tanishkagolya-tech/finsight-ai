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