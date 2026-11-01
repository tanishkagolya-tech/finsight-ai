import yfinance as yf

for symbol, name in [("BTC-USD", "btc"), ("ETH-USD", "eth")]:
    df = yf.download(symbol, start="2020-01-01", progress=False)
    df.columns = df.columns.get_level_values(0)  # flatten the double header
    df.to_csv(f"data/{name}.csv")
    print(name, df.shape, df.index.min(), df.index.max())