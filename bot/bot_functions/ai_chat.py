from aiogram.fsm.context import FSMContext

from config import States
from init import bot
from translation import get_language_for_telegram_id as _l,  translate_string as _


async def begin_ai_chat(chat_id: int | str, state: FSMContext):
    await state.set_state(States.ai_chat)
    language = await _l(chat_id)
    await bot.send_message(chat_id=chat_id,
                           text=_("Задайте свой вопрос и я попробую найти что-то связанное в моей базе знаний!",
                                  language=language))
