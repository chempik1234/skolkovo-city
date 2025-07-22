from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import States
from init import bot
from keyboards import language_keyboards
from translation import translate_string as _, get_language_for_telegram_id


async def make_user_choose_language(user_id: int | str):
    language = await get_language_for_telegram_id(user_id)
    await bot.send_message(chat_id=user_id, text=_("Выберите язык", language)+":", reply_markup=language_keyboards)
