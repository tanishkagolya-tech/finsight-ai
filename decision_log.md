# Decision Log

## Day 1
- Python 3.12 chosen over 3.13: ML libraries (SHAP, hmmlearn, torch) support lags behind the newest Python release.
- Virtual environment (.venv): isolates dependencies so the project is reproducible.
- data/ is in .gitignore: raw data is large and can be re-downloaded with yfinance.