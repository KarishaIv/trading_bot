from services.images_analysis.fetch_data import fetch_foreign_data, fetch_moex_data
import matplotlib.pyplot as plt
import os

def generate_cnn_analysis_image(ticker: str, start_date: str, end_date: str, stock_type: str,
                                sma_fast: int = 3, sma_slow: int = 7) -> (str, float):
    if stock_type == "foreign":
        df = fetch_foreign_data(ticker, start_date, end_date)
        if df is None or df.empty:
            print(f"Нет данных для {ticker} с Yahoo Finance")
            return None, None
        df = df.copy()
        df.rename(columns={"Close": "close"}, inplace=True)

    else:
        df = fetch_moex_data(ticker, days=45)
        if df is None or df.empty:
            print(f"Нет данных для {ticker} с MOEX")
            return None, None
        df = df.copy()
        df.rename(columns={"Close": "close"}, inplace=True)

    df["sma_fast"] = df["close"].rolling(sma_fast).mean()
    df["sma_slow"] = df["close"].rolling(sma_slow).mean()

    draw_window = 30
    if len(df) < draw_window:
        print("Недостаточно данных для построения графика")
        return None, None

    window = df.iloc[-draw_window:]
    if stock_type == "foreign":
        date_str = window.index[-1].strftime("%Y_%m_%d")
    else:
        date_str = window.index[-2].strftime("%Y_%m_%d")
    image_dir = "services/images_analysis/temp_images"
    os.makedirs(image_dir, exist_ok=True)
    filename = f"{ticker}_{date_str}.png"
    filepath = os.path.join(image_dir, filename)

    plt.figure(figsize=(3, 3))
    plt.plot(window["close"], label="Close")
    plt.plot(window["sma_fast"], label="SMA Fast")
    plt.plot(window["sma_slow"], label="SMA Slow")
    plt.legend()
    plt.axis("off")
    plt.savefig(filepath, bbox_inches="tight")
    plt.close()

    last_price = window["close"].iloc[-1]
    return filepath, last_price