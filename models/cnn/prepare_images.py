import os
import pandas as pd
import matplotlib.pyplot as plt

def generate_cnn_training_images(ticker: str,
                                  csv_dir: str = "tickers_info",
                                  output_dir: str = "images/training_dataset",
                                  draw_window: int = 5,
                                  sma_fast: int = 3,
                                  sma_slow: int = 7):
    filepath = os.path.join(csv_dir, f"{ticker}.csv")
    if not os.path.exists(filepath):
        print(f"Файл не найден: {filepath}")
        return
    df = pd.read_csv(filepath, parse_dates=["Datetime"])

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=["close"], inplace=True)

    df["sma_fast"] = df["close"].rolling(sma_fast).mean()
    df["sma_slow"] = df["close"].rolling(sma_slow).mean()

    os.makedirs(os.path.join(output_dir, "0"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "1"), exist_ok=True)

    for i in range(len(df) - draw_window - 1):
        window = df.iloc[i:i + draw_window]
        next_day_close = df.iloc[i + draw_window]["close"]

        if window[["close", "sma_fast", "sma_slow"]].isnull().any().any() or pd.isna(next_day_close):
            continue

        closes = window["close"].tolist()
        fast = window["sma_fast"].tolist()
        slow = window["sma_slow"].tolist()
        date = window["Datetime"].iloc[-1].strftime("%Y_%m_%d")

        plt.figure(figsize=(3, 3))
        plt.plot(closes, label="Close")
        plt.plot(fast, label="SMA Fast")
        plt.plot(slow, label="SMA Slow")
        plt.legend()
        plt.axis("off")

        label = "1" if next_day_close > closes[-1] else "0"
        filename = f"{ticker}_{date}.png"
        save_path = os.path.join(output_dir, label, filename)

        plt.savefig(save_path)
        plt.close()

    print(f"{ticker} — изображения сохранены")
if __name__ == "__main__":
    tickers = [
        "AAPL", "NVDA", "TSLA", "BABA", "GOOGL", "NFLX", "AMZN", "UBER", "META", "WBD"
    ]
    for t in tickers:
        generate_cnn_training_images(ticker=t, draw_window=30)
