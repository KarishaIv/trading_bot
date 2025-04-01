from aiogram import Router, types
from aiogram.enums import ParseMode
from services.news.news_analysis import get_top_5_news, get_news_with_sentiment
from config import user_data
from keyboards.reply import get_foreign_stock_keyboard

router = Router()

@router.callback_query()
async def news_callbacks(query: types.CallbackQuery):
    user_id = query.from_user.id
    data = query.data

    if user_id not in user_data or not user_data[user_id].get("ticker"):
        await query.message.answer("Сначала введите тикер компании")
        return

    ticker = user_data[user_id]["ticker"]

    await query.message.answer("🔄 Новости обрабатываются, пожалуйста, подождите...")


    if data == "top5_news":
        result = get_top_5_news(ticker)
    elif data == "analyze_news":
        result = get_news_with_sentiment(ticker)
    else:
        result = "Неизвестный запрос"

    await query.message.answer(result, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=get_foreign_stock_keyboard()
)
    return