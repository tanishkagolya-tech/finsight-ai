\# EDA Findings (Week 2)



| # | Finding | Evidence | So what for the model |

|---|---------|----------|-----------------------|

| 1 | Prices are not stationary; returns are | ADF: BTC log price p=0.36, returns p<0.0001 | |

| 2 | Returns have fat tails and negative skew | Excess kurtosis BTC 22.3, ETH 15.8; worst day about 15 std below the mean | |

| 3 | Volatility clusters | ACF of squared returns positive at all 10 lags; crashes followed by rebounds | |

| 4 | Fraud is extremely rare | 473 of 283,726 rows (0.167%) after dedup | |

| 5 | Fraud amounts are skewed and non-monotonic | Median $9.25 vs $22.00; fraud rate U-shaped by amount | |

| 6 | Data-quality issues found | 1,081 duplicates (19 fraud); 2021-02-26 volume looks wrong; last day incomplete | |

| 7 | BTC and ETH correlation | <your Pearson on returns, and the interval> | |

| 8 | ETH is more volatile than BTC | <your std ratio and p-value> | |

| 9 | v14/v17 separate fraud far better than amount | <your effect sizes> | |

