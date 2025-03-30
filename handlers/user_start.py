from aiogram import Router, types
from aiogram.filters import Command
from keyboards.reply import get_stock_type_keyboard
from config import user_data
router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"type": None, "ticker": None}
    await message.answer("👋 Выберите акции каких компаний вас интересуют:", reply_markup=get_stock_type_keyboard())
