import os
import yfinance as yf

def get_data_yahoo(ticker: str, start: str, end: str, save_dir: str = "tickers_info"):
    os.makedirs(save_dir, exist_ok=True)

    print(f"Загружаем данные для {ticker} с {start} по {end}...")

    try:
        df = yf.download(ticker, start=start, end=end, interval="1d")
        if df.empty:
            print(f"Нет данных для {ticker}")
            return False

        df.reset_index(inplace=True)
        df.rename(columns={
            "Date": "Datetime",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }, inplace=True)

        df = df[["Datetime", "open", "high", "low", "close", "volume"]]
        path = os.path.join(save_dir, f"{ticker}.csv")
        df.to_csv(path, index=False, encoding='utf-8', sep=',')

        print(f"Данные сохранены: {path}")
        return True

    except Exception as e:
        print(f"Ошибка при загрузке {ticker}: {e}")
        return False

if __name__ == "__main__":
    tickers = [
        "AAPL", "NVDA", "TSLA", "BABA", "GOOGL", "NFLX", "AMZN", "UBER", "META", "WBD"
    ]

    start_date = "2014-03-10"
    end_date = "2024-03-10"

    for ticker in tickers:
        get_data_yahoo(ticker, start=start_date, end=end_date)
