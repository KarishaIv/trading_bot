from tensorflow.keras import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from models.lstm.prepare_data import fetch_historical_stock_data_yahoo, series_to_supervised
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText

#чтобы снова не обучать

exit(777)
def train_stock_model(tickers):
    df = fetch_historical_stock_data_yahoo(tickers)

    if df is None or df.empty:
        return None, None

    dataset = df[['Open', 'High', 'Low', 'Close', 'ma7', 'MACD', 'upper_band', 'lower_band']].copy()
    values = dataset.values.astype('float32')

    scaler = MinMaxScaler(feature_range=(0, 1))
    values_scaled = scaler.fit_transform(values)

    reframed = series_to_supervised(values_scaled, 5, 1)
    transformed_values = reframed.values
    train_size = int(len(transformed_values) * 0.7)
    train, test = transformed_values[:train_size, :], transformed_values[train_size:, :]

    n_features = len(dataset.columns)
    train_X, train_y = train[:, :-n_features], train[:, -n_features]
    test_X, test_y = test[:, :-n_features], test[:, -n_features]

    train_X = train_X.reshape((train_X.shape[0], 5, n_features))
    test_X = test_X.reshape((test_X.shape[0], 5, n_features))

    model = Sequential([
        LSTM(160, return_sequences=True, input_shape=(5, n_features)),
        Dropout(0.2),
        LSTM(80, return_sequences=True),
        Dropout(0.2),
        LSTM(40),
        Dense(1, activation='relu'),
    ])

    model.compile(loss='mean_squared_error', optimizer='adam')
    model.summary()

    model.fit(
        train_X, train_y,
        epochs=50,
        batch_size=16,
        validation_data=(test_X, test_y),
        verbose=2,
        shuffle=False
    )

    model.save("lstm.keras")

    predicted = model.predict(test_X)

    mse = mean_squared_error(test_y, predicted)
    mae = mean_absolute_error(test_y, predicted)

    print(f"Оценка на тесте:")
    print(f"MSE: {mse:.6f}")
    print(f"MAE: {mae:.6f}")

    plt.figure(figsize=(10, 4))
    plt.plot(test_y[:100], label="Actual")
    plt.plot(predicted[:100], label="Predicted")
    plt.legend()
    plt.title("LSTM Predictions vs Actual")
    plt.grid(True)

    textstr = f"MSE: {mse:.6f}\nMAE: {mae:.6f}"
    anchored_text = AnchoredText(textstr, loc='lower right', prop={'size': 10},
                                 bbox_to_anchor=(1, 1),
                                 bbox_transform=plt.gca().transAxes,
                                 frameon=True)
    plt.gca().add_artist(anchored_text)

    plt.tight_layout()
    plt.savefig("lstm_test_predictions.png", dpi=150)
    plt.show()
    return model

tickers = [
    "AAPL", "NVDA", "TSLA", "BABA", "GOOGL", "NFLX", "AMZN", "UBER", "META", "WBD"
]

model = train_stock_model(tickers)
