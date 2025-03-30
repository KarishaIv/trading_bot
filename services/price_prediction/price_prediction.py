import numpy as np
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
from services.price_prediction.load_moex_data import load_moex_data
from models.lstm.prepare_data import fetch_historical_stock_data_yahoo

def predict_price(model, ticker, target_date, stock_type):
    if stock_type == 'foreign':
        df = fetch_historical_stock_data_yahoo([ticker], target_date - timedelta(days=30), target_date)
    else:
        df = load_moex_data(ticker, target_date - timedelta(days=30), target_date)

    if df is None or len(df) < 6:
        return "Нет данных", None

    features = ['Open', 'High', 'Low', 'Close', 'ma7', 'MACD', 'upper_band', 'lower_band']
    df = df[features].values.astype('float32')

    scaler = MinMaxScaler()
    df_scaled = scaler.fit_transform(df)

    past_data = df_scaled[-5:].reshape(1, 5, len(features))
    predicted_scaled = model.predict(past_data)

    predicted = np.zeros((1, len(features)))
    predicted[:, 3] = predicted_scaled[:, 0]
    predicted_price = scaler.inverse_transform(predicted)[:, 3][0]

    actual_price = df[-1][3]
    return predicted_price, actual_price
