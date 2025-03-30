import numpy as np

def calculate_indicators(df):
    df['SMA10'] = df['Close'].rolling(window=10).mean()
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['EMA10'] = df['Close'].ewm(span=10, adjust=False).mean()
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()

    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['RSI_Change'] = df['RSI'].diff()

    # MACD
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Стохастик
    df['L14'] = df['Low'].rolling(window=14).min()
    df['H14'] = df['High'].rolling(window=14).max()
    df['%K'] = (df['Close'] - df['L14']) / (df['H14'] - df['L14']) * 100
    df['%D'] = df['%K'].rolling(window=3).mean()

    # CCI
    df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['CCI'] = (df['TP'] - df['TP'].rolling(window=20).mean()) / (0.015 * df['TP'].rolling(window=20).std())

    # ADX
    df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
    df['+DM'] = np.where((df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']), df['High'] - df['High'].shift(1), 0)
    df['-DM'] = np.where((df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)), df['Low'].shift(1) - df['Low'], 0)
    df['+DI'] = 100 * (df['+DM'].rolling(window=14).mean() / df['TR'].rolling(window=14).mean())
    df['-DI'] = 100 * (df['-DM'].rolling(window=14).mean() / df['TR'].rolling(window=14).mean())
    df['ADX'] = 100 * abs((df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI'])).rolling(window=14).mean()

    return df
