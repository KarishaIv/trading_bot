import yfinance as yf
import pandas as pd
from tensorflow.keras import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from datetime import datetime


def fetch_historical_stock_data_yahoo(tickers, start_date=datetime(2014, 3, 10), end_date=datetime(2024, 3, 10)):
    end_date = end_date
    start_date = start_date
    all_data = []

    for ticker in tickers:
        df = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'),
                         end=end_date.strftime('%Y-%m-%d'), interval="1d")

        if df.empty:
            print(f"Нет данных для {ticker}")
            continue

        df.reset_index(inplace=True)
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        df = df[['Date', 'Open', 'High', 'Low', 'Close']]
        df.set_index("Date", inplace=True)

        df['ma7'] = df['Close'].rolling(window=7, min_periods=1).mean()

        df['ema12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['ema12'] - df['ema26']

        df['std20'] = df['Close'].rolling(window=20, min_periods=1).std()
        df['upper_band'] = df['ma7'] + (df['std20'] * 2)
        df['lower_band'] = df['ma7'] - (df['std20'] * 2)

        df.drop(columns=['ema12', 'ema26', 'std20'], inplace=True)
        df.dropna(subset=['Close'], inplace=True)
        df.fillna(method="bfill", inplace=True)

        df['Ticker'] = ticker
        all_data.append(df)

    return pd.concat(all_data) if all_data else None

def series_to_supervised(data, n_in=5, n_out=1, dropnan=True):
    n_vars = data.shape[1]
    df = pd.DataFrame(data)
    cols, names = [], []

    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [f'var{j+1}(t-{i})' for j in range(n_vars)]

    for i in range(0, n_out):
        cols.append(df.shift(-i))
        names += [f'var{j+1}(t+{i})' for j in range(n_vars)]

    agg = pd.concat(cols, axis=1)
    agg.columns = names

    if dropnan:
        agg.dropna(inplace=True)

    return agg