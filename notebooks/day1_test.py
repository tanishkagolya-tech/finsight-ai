import yfinance as yf

df = yf.download("BTC-USD", start="2020-01-01", progress=False)
print(df.head())
print(df.shape)
df.to_csv("data/btc_raw.csv")