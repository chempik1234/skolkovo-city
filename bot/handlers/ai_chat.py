import structlog
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import States
from init.init_2 import ai_chat_service
from translation import translate_string as _, get_language_for_telegram_id as _l

logger = structlog.get_logger(name="handlers.ai_chat")

router = Router()


@router.message(States.ai_chat)
async def ai_chat_message_handler(message: Message, state: FSMContext):
    question_text = message.text
    try:
        question, answer = await ai_chat_service.get_related_question_from_db(question_text)  # message.from_user.id,
        await message.answer(text=f"{question}\n\n{answer}")
    except Exception as e:
        logger.error("error while asking bot a question", exc_info=e, extra_data={"question": question_text})
        await message.answer(_("Не удалось получить ответ на вопрос", await _l(message.from_user.id)))
