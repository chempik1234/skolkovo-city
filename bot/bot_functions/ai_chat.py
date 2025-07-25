import asyncio

import structlog
from aiogram.fsm.context import FSMContext

from config import States
from init import bot
from init.ai_chat_service import ai_chat_service
from init.init_0 import bot_config
from keyboards import ask_ai_keyboard
from translation import get_language_for_telegram_id as _l, translate_string as _

logger = structlog.get_logger(__name__)


async def begin_ai_chat(chat_id: int | str, state: FSMContext):
    await state.set_state(States.ai_embedding)
    language = await _l(chat_id)
    await bot.send_message(chat_id=chat_id,
                           text=_("Задайте свой вопрос и я попробую найти что-то связанное в моей базе знаний!",
                                  language=language))


async def unknown_question(chat_id: int | str, question: str, be_silent: bool = False):
    logger.info("received an unanswered question", question=question)

    asyncio.create_task(ai_chat_service.create_new_question(chat_id, question))

    if not be_silent:
        language = await _l(chat_id)
        await bot.send_message(
            chat_id=chat_id,
            text=_(bot_config.EMBEDDING_NOT_FOUND_MESSAGE_RU,   # look I'm too stupid for a well-made i18n
                   language),                                   # rewrite it if you can please
            reply_markup=ask_ai_keyboard(language),
        )
