import matplotlib.pyplot as plt
import pandas as pd
from aiogram.types import FSInputFile
from services.technical_indicators.load_data import fetch_foreign_data, fetch_moex_data
from services.technical_indicators.calculate_indicators import calculate_indicators
from keyboards.reply import get_keyboard_for_user
from aiogram import Bot


def evaluate_signals(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    ratings = {}

    ratings['SMA10'] = 1 if latest['SMA10'] < latest['Close'] else -1
    ratings['SMA20'] = 1 if latest['SMA20'] < latest['Close'] else -1
    ratings['EMA10'] = 1 if latest['EMA10'] < latest['Close'] else -1
    ratings['EMA20'] = 1 if latest['EMA20'] < latest['Close'] else -1

    if latest['RSI'] < 30 and latest['RSI_Change'] > 0:
        ratings['RSI'] = 1
    elif latest['RSI'] > 70 and latest['RSI_Change'] < 0:
        ratings['RSI'] = -1
    else:
        ratings['RSI'] = 0


    ratings['MACD'] = 1 if latest['MACD'] > latest['Signal'] else -1

    ratings['Stoch'] = 1 if latest['%K'] < 20 and prev['%K'] < prev['%D'] and latest['%K'] > latest['%D'] else -1 if latest['%K'] > 80 and prev['%K'] > prev['%D'] and latest['%K'] < latest['%D'] else 0

    ratings['CCI'] = 1 if latest['CCI'] < -100 and latest['CCI'] > prev['CCI'] else -1 if latest['CCI'] > 100 and latest['CCI'] < prev['CCI'] else 0

    ratings['ADX'] = 1 if latest['ADX'] > 20 and latest['+DI'] > latest['-DI'] else -1 if latest['ADX'] > 20 and latest['+DI'] < latest['-DI'] else 0

    total_score = sum(ratings.values()) / len(ratings)

    if total_score >= 0.1:
        overall_rating = "🔼 Покупка"
    else:
        overall_rating = "🔽 Продажа"

    return ratings, overall_rating

async def send_indicator_analysis(bot: Bot, user_id, ticker, stock_type):
    if stock_type == "foreign":
        df = fetch_foreign_data(ticker)
    else:
        df = fetch_moex_data(ticker)

    if df is None or df.empty:
        await bot.send_message(user_id, f"Нет данных для {ticker}.")
        return

    df = calculate_indicators(df)
    ratings, overall_rating = evaluate_signals(df)

    df_ratings = pd.DataFrame(ratings.items(), columns=['Индикатор', 'Сигнал'])
    df_ratings['Сигнал'] = df_ratings['Сигнал'].map({1: "Покупка", -1: "Продажа", 0: "Нейтрально"})

    plt.figure(figsize=(10, 5))
    plt.bar(df_ratings['Индикатор'], df_ratings['Сигнал'].map({"Покупка": 1, "Продажа": -1, "Нейтрально": 0}),
            color=['green' if x == 'Покупка' else 'red' if x == 'Продажа' else 'gray' for x in df_ratings['Сигнал']])
    plt.axhline(0, color="black", linestyle="--")
    plt.title(f"Анализ технических индикаторов для {ticker}")
    plt.xticks(rotation=45)
    plt.xlabel("Индикаторы")
    plt.ylabel("Сигнал")
    plt.grid(True)

    image_path = f"/tmp/{ticker}_indicators.png"
    plt.savefig(image_path)
    plt.close()

    await bot.send_photo(user_id, FSInputFile(image_path),     caption=(
        f"📊 <b>Анализ технических индикаторов {ticker}</b>\n\n"
        "<b>Индикаторы</b>: SMA, EMA, RSI, MACD, Стохастик, CCI, ADX\n\n"
        "🟩 <b>Покупка</b> – сигнал к росту\n"
        "🟥 <b>Продажа</b> – сигнал к падению\n"
        "⬜️ <b>Нейтрально</b> – неопределённость\n\n"
        f"🔎 <b>Общий вывод</b>: {overall_rating}"
    ),
    parse_mode="HTML", reply_markup=get_keyboard_for_user(user_id))

