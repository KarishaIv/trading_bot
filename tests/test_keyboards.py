from keyboards.reply import (
    get_stock_type_keyboard,
    get_foreign_stock_keyboard,
    get_russian_stock_keyboard,
    get_news_keyboard,
)

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup


def test_get_stock_type_keyboard_structure():
    kb = get_stock_type_keyboard()
    assert isinstance(kb, ReplyKeyboardMarkup)
    assert len(kb.keyboard) == 2
    assert "Российские" in kb.keyboard[0][0].text
    assert "Иностранные" in kb.keyboard[1][0].text


def test_get_foreign_stock_keyboard_contains_all_options():
    kb = get_foreign_stock_keyboard()
    texts = [btn.text for row in kb.keyboard for btn in row]
    assert "ℹ️ Информация о компании" in texts
    assert "📰 Анализ новостей" in texts
    assert "📈 Прогноз цены" in texts
    assert "🖼️ Анализ графика" in texts
    assert "📊 Анализ тех индикаторов" in texts
    assert "🔙 Вернуться к выбору акций" in texts


def test_get_russian_stock_keyboard_contains_all_options():
    kb = get_russian_stock_keyboard()
    texts = [btn.text for row in kb.keyboard for btn in row]
    assert "📰 Анализ новостей" not in texts
    assert "📈 Прогноз цены" in texts
    assert "🖼️ Анализ графика" in texts
    assert "📊 Анализ тех индикаторов" in texts
    assert "🔙 Вернуться к выбору акций" in texts


def test_get_news_keyboard_structure():
    kb = get_news_keyboard()
    assert isinstance(kb, InlineKeyboardMarkup)
    assert len(kb.inline_keyboard) == 2
    assert kb.inline_keyboard[0][0].callback_data == "top5_news"
    assert kb.inline_keyboard[1][0].callback_data == "analyze_news"



def test_back_button_exists_in_all_keyboards():
    back_text = "🔙 Вернуться к выбору акций"

    russian_kb = get_russian_stock_keyboard()
    russian_texts = [btn.text for row in russian_kb.keyboard for btn in row]
    assert back_text in russian_texts

    foreign_kb = get_foreign_stock_keyboard()
    foreign_texts = [btn.text for row in foreign_kb.keyboard for btn in row]
    assert back_text in foreign_texts
