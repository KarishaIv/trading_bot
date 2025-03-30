import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_foreign_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = yf.download(ticker, start=start_date, end=end_date, interval="1d")
    if df.empty:
        return None
    df.reset_index(inplace=True)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    df = df[['Date', 'Close']]
    df.set_index("Date", inplace=True)
    return df


def fetch_moex_data(ticker: str, days: int = 45) -> pd.DataFrame:
    end = datetime.today()
    start = end - timedelta(days=days)

    url = f"https://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}/candles.json"
    params = {
        "from": start.strftime("%Y-%m-%d"),
        "till": end.strftime("%Y-%m-%d"),
        "interval": 24,
        "iss.meta": "off"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Ошибка: {response.status_code}")
        return None

    data = response.json()
    if "candles" not in data or "data" not in data["candles"]:
        return None

    columns = data["candles"]["columns"]
    df = pd.DataFrame(data["candles"]["data"], columns=columns)
    df = df.rename(columns={"begin": "Date", "open": "Open", "high": "High", "low": "Low", "close": "Close"})
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    return df[['Open', 'High', 'Low', 'Close']]