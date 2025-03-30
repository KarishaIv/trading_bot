from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import user_data

def get_stock_type_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇷🇺 Российские компании")],
            [KeyboardButton(text="🇺🇸 Иностранные компании")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_foreign_stock_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ℹ️ Информация о компании")],
            [KeyboardButton(text="📰 Анализ новостей")],
            [KeyboardButton(text="📈 Прогноз цены")],
            [KeyboardButton(text="🖼️ Анализ графика")],
            [KeyboardButton(text="📊 Анализ тех индикаторов")],
            [KeyboardButton(text="🔙 Вернуться к выбору акций")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_russian_stock_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📈 Прогноз цены")],
            [KeyboardButton(text="🖼️ Анализ графика")],
            [KeyboardButton(text="📊 Анализ тех индикаторов")],
            [KeyboardButton(text="🔙 Вернуться к выбору акций")]

        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_news_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📜 Последние 5 новостей", callback_data="top5_news")],
            [InlineKeyboardButton(text="📊 Анализ 10 новостей", callback_data="analyze_news")],
        ]
    )

def get_keyboard_for_user(user_id):
    stock_type = user_data[user_id]["type"]
    if stock_type == "foreign":
        return get_foreign_stock_keyboard()
    else:
        return get_russian_stock_keyboard()

