import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta


def fetch_foreign_data(ticker: str, period="3mo"):
    df = yf.download(ticker, period=period, interval="1d")
    df.reset_index(inplace=True)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    df = df[['Date', 'Open', 'High', 'Low', 'Close']]
    df.set_index("Date", inplace=True)
    return df

def fetch_moex_data(ticker: str):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=90)

    url = f"https://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}/candles.json"
    params = {
        "from": start_date.strftime("%Y-%m-%d"),
        "till": end_date.strftime("%Y-%m-%d"),
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
