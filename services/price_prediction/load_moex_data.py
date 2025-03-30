import requests
import pandas as pd


def load_moex_data(ticker, start, end):
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
        print("Нет данных от MOEX")
        return None

    columns = data["candles"]["columns"]
    df = pd.DataFrame(data["candles"]["data"], columns=columns)
    df = df.rename(columns={"begin": "Date", "open": "Open", "high": "High", "low": "Low", "close": "Close"})
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    df['ma7'] = df['Close'].rolling(window=7, min_periods=1).mean()
    df['ema12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['ema26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['ema12'] - df['ema26']
    df['std20'] = df['Close'].rolling(window=20, min_periods=1).std()
    df['upper_band'] = df['ma7'] + 2 * df['std20']
    df['lower_band'] = df['ma7'] - 2 * df['std20']

    df.drop(columns=['ema12', 'ema26', 'std20'], inplace=True)
    df.dropna(inplace=True)

    return df[['Open', 'High', 'Low', 'Close', 'ma7', 'MACD', 'upper_band', 'lower_band']]
