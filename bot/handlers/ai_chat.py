import numpy
import structlog
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot_functions.ai_chat import unknown_question
from config import States
from init.init_0 import bot_config
from init.init_2 import ai_chat_service
from keyboards import ai_response_keyboard
from translation import translate_string as _, get_language_for_telegram_id as _l

logger = structlog.get_logger(name="handlers.ai_chat")

router = Router()


@router.message(States.ai_chat)
async def ai_chat_message_handler(message: Message, state: FSMContext):
    question_text = message.text
    language = await _l(message.from_user.id)

    try:
        question, answer, value = await ai_chat_service.get_related_question_from_db(question_text)  # message.from_user.id,

        # we know it's a bad answer
        if not value or isinstance(value, numpy.float64) and float(value) < bot_config.EMBEDDING_THRESHOLD:
            await unknown_question(message.chat.id, question_text)
        # we let user say if he likes it
        else:
            await message.answer(text=f"{question}\n\n{answer}",
                                 reply_markup=ai_response_keyboard(question_text, language))

    except Exception as e:
        logger.error("error while asking bot a question", exc_info=e, extra_data={"question": question_text})

        await message.answer(_("Не удалось получить ответ на вопрос", language))


@router.callback_query(F.data.startswith("bad_answer_"))
async def bad_answer_callback(callback: CallbackQuery, state: FSMContext):
    message_text = callback.data.replace("bad_answer_", "", 1)
    await unknown_question(callback.message.chat.id, message_text)
