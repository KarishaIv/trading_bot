import numpy as np
import yfinance as yf
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import LSTM, Dropout

n_steps = 5
n_features = 8
tickers = [
    "AAPL", "NVDA", "TSLA", "BABA", "GOOGL", "NFLX", "AMZN", "UBER", "META", "WBD"
]
model_weights_path = "../lstm/lstm.keras"

def build_lstm_feature_extractor(input_shape):
    inputs = Input(shape=input_shape, name="lstm_input")
    x = LSTM(160, return_sequences=True)(inputs)
    x = Dropout(0.2)(x)
    x = LSTM(80, return_sequences=True)(x)
    x = Dropout(0.2)(x)
    x = LSTM(40)(x)
    return Model(inputs, x, name="lstm_feature_extractor")

lstm_feature_extractor = build_lstm_feature_extractor((n_steps, n_features))
lstm_feature_extractor.load_weights(model_weights_path, skip_mismatch=True)

def fetch_historical_stock_data_yahoo(ticker):
    df = yf.download(ticker, start=datetime(2014, 3, 10), end=datetime(2024, 3, 10), interval="1d")
    df = df[['Open', 'High', 'Low', 'Close']]
    df['ma7'] = df['Close'].rolling(window=7, min_periods=1).mean()
    df['ema12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['ema26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['ema12'] - df['ema26']
    df['std20'] = df['Close'].rolling(window=20, min_periods=1).std()
    df['upper_band'] = df['ma7'] + (df['std20'] * 2)
    df['lower_band'] = df['ma7'] - (df['std20'] * 2)
    df.drop(columns=['ema12', 'ema26', 'std20'], inplace=True)
    df.dropna(inplace=True)
    return df

def series_to_supervised(data, n_in=5, n_out=1, dropnan=True):
    n_vars = data.shape[1]
    df = pd.DataFrame(data)
    cols = []
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
    for i in range(0, n_out):
        cols.append(df.shift(-i))
    agg = pd.concat(cols, axis=1)
    if dropnan:
        agg.dropna(inplace=True)
    return agg

all_features = []
all_labels = []

for ticker in tickers:
    df = fetch_historical_stock_data_yahoo(ticker)
    if df is None or df.empty:
        continue
    dataset = df[['Open', 'High', 'Low', 'Close', 'ma7', 'MACD', 'upper_band', 'lower_band']]
    values = dataset.values.astype('float32')
    scaler = MinMaxScaler()
    values_scaled = scaler.fit_transform(values)
    reframed = series_to_supervised(values_scaled, n_steps, 1)
    transformed = reframed.values
    train_size = int(len(transformed) * 0.7)
    train = transformed[:train_size]
    train_X = train[:, :-n_features]
    train_y = train[:, -n_features]
    train_X = train_X.reshape((train_X.shape[0], n_steps, n_features))
    features = lstm_feature_extractor.predict(train_X, batch_size=16, verbose=0)
    all_features.append(features)
    all_labels.append(train_y)

lstm_features = np.vstack(all_features)
lstm_labels = np.concatenate(all_labels)

np.save("lstm_features.npy", lstm_features)
np.save("lstm_labels.npy", lstm_labels)


