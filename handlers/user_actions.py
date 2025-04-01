from aiogram.enums import ParseMode
from aiogram import Router, types

from keyboards.reply import (
    get_foreign_stock_keyboard,
    get_russian_stock_keyboard,
    get_stock_type_keyboard
)
import yfinance as yf
from services.stock_info import get_stock_info
from services.price_prediction.price_prediction import predict_price
from services.technical_indicators.indicator_analysis import send_indicator_analysis
from config import user_data
import tensorflow as tf
from datetime import datetime, timedelta
from config import  MODEL_PATH_LSTM
from keyboards.reply import get_news_keyboard
from aiogram.types import FSInputFile
from services.images_analysis.generate_image import generate_cnn_analysis_image
from services.images_analysis.prediction_cnn import predict_cnn_from_image
from keyboards.reply import get_keyboard_for_user
import requests


lstm_model = tf.keras.models.load_model(MODEL_PATH_LSTM)
router = Router()

def is_valid_yahoo_ticker(ticker: str) -> bool:
    try:
        info = yf.Ticker(ticker).info
        return bool(info) and "longName" in info
    except Exception:
        return False


def is_valid_moex_ticker(ticker: str) -> bool:
    ticker = ticker.upper()
    end = datetime.today()
    start = end - timedelta(days=1)

    url = f"https://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}/candles.json"
    params = {
        "from": start.strftime("%Y-%m-%d"),
        "till": end.strftime("%Y-%m-%d"),
        "interval": 24,
        "iss.meta": "off"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code != 200:
            return False

        data = response.json()
        return bool(data.get("candles", {}).get("data"))

    except Exception:
        return False


@router.message()
async def handle_user_input(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip().upper()


    if user_id not in user_data:
        user_data[user_id] = {"type": None, "ticker": None}
        await message.answer("👋 Выберите акции каких компаний вас интересуют:", reply_markup=get_stock_type_keyboard())
        return

    if text == "🇷🇺 РОССИЙСКИЕ КОМПАНИИ":
        user_data[user_id]["type"] = "russian"
        user_data[user_id]["ticker"] = None
        await message.answer("Введите тикер российской компании (например, SBER, GAZP):")
        return

    elif text == "🇺🇸 ИНОСТРАННЫЕ КОМПАНИИ":
        user_data[user_id]["type"] = "foreign"
        user_data[user_id]["ticker"] = None
        await message.answer("Введите тикер иностранной компании (например, AAPL, TSLA):")
        return

    if user_data[user_id]["type"] is None:
        await message.answer("Сначала выберите, какие акции вас интересуют:")
        return


    if user_data[user_id]["ticker"] is None:
        if user_data[user_id]["type"] == "foreign":
            if is_valid_yahoo_ticker(text):
                user_data[user_id]["ticker"] = text
                await message.answer(f"✅ Тикер {text} сохранен! Выберите действие:", reply_markup=get_foreign_stock_keyboard())
            else:
                await message.answer("Я не нашел этот тикер. Попробуйте еще раз.")
        else:
            if is_valid_moex_ticker(text):
                user_data[user_id]["ticker"] = text
                await message.answer(f"✅ Тикер {text} сохранен! Выберите действие:",
                                     reply_markup=get_russian_stock_keyboard())
            else:
                await message.answer("Я не нашёл этот тикер. Попробуйте ещё раз.")
        return

    ticker_symbol = user_data[user_id]["ticker"]
    stock_type = user_data[user_id]["type"]


    if text == "ℹ️ ИНФОРМАЦИЯ О КОМПАНИИ":
        if stock_type == "foreign":
            company_info = get_stock_info(ticker_symbol)
            await message.answer(company_info, parse_mode=ParseMode.HTML, reply_markup=get_foreign_stock_keyboard())
        else:
            await message.answer("Информация доступна только для иностранных акций", reply_markup=get_foreign_stock_keyboard())
    elif text == "📊 АНАЛИЗ ТЕХ ИНДИКАТОРОВ":
        await send_indicator_analysis(message.bot, user_id, ticker_symbol, stock_type)
        return
    elif text == "📈 ПРОГНОЗ ЦЕНЫ":
        if lstm_model is None:
            await message.answer("Ошибка: LSTM модель не загружена.")
            return

        target_date = datetime.today()

        predicted_price, actual_price = predict_price(lstm_model, ticker_symbol, target_date, stock_type)


        if predicted_price == "Нет данных":
            await message.answer(f"Недостаточно данных для предсказания цены {ticker_symbol}.", reply_markup=get_keyboard_for_user(user_id))
            return

        response = (
            f"📈 <b>Прогноз цены {ticker_symbol} на завтра:</b>\n\n"
            f"🔮 <b>Предсказанная цена:</b> {predicted_price:.2f} {('руб.' if stock_type == 'russian' else '$')}\n"
            f"💵 <b>Последняя известная цена:</b> {actual_price:.2f} {('руб.' if stock_type == 'russian' else '$')}\n"
        )
        await message.answer(response, parse_mode=ParseMode.HTML, reply_markup=get_keyboard_for_user(user_id))



    elif text == "🖼️ АНАЛИЗ ГРАФИКА":
        if user_id not in user_data or not user_data[user_id].get("ticker"):
            await message.answer("Сначала введите тикер компании")
            return

        ticker = user_data[user_id]["ticker"]
        stock_type = user_data[user_id]["type"]
        end_date = datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.today() - timedelta(days=45)).strftime("%Y-%m-%d")

        image_path, last_price = generate_cnn_analysis_image(ticker, start_date, end_date, stock_type)
        if image_path is None:
            await message.answer(f"Не удалось сформировать график для {ticker}.")
            return

        prediction = predict_cnn_from_image(image_path)
        forecast = "Цена поднимется" if prediction == "UP" else "Цена упадет"
        caption = (
            f"📊 Анализ графика {ticker}\n\n"
            f"🔮 Прогноз: {forecast}\n"
        )
        await message.answer_photo(photo=FSInputFile(image_path), caption=caption, parse_mode=ParseMode.HTML, reply_markup=get_keyboard_for_user(user_id))


    elif text == "📰 АНАЛИЗ НОВОСТЕЙ":
        await message.answer("Выберите вариант анализа новостей:", reply_markup=get_news_keyboard())

    elif text == "🔙 ВЕРНУТЬСЯ К ВЫБОРУ АКЦИЙ":
        user_data[user_id] = {"type": None, "ticker": None}
        await message.answer("👋 Выберите акции каких компаний вас интересуют:", reply_markup=get_stock_type_keyboard())
        return

    else:
        await message.answer("Неизвестная команда. Выберите действие из меню.")


