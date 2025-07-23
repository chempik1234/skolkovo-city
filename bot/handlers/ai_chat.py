import asyncio

import numpy
import structlog
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot_functions.ai_chat import unknown_question, ask_chat_bot, new_answer_message
from config import States
from init.init_0 import bot_config
from init.init_2 import ai_chat_service, bot
from keyboards import ai_response_keyboard
from translation import translate_string as _, get_language_for_telegram_id as _l
from utils import get_logging_extra

logger = structlog.get_logger(name="handlers.ai_chat")

router = Router()


@router.message(States.ai_embedding)
async def ai_chat_message_handler(message: Message, state: FSMContext):
    question_text = message.text

    user_id = message.from_user.id
    logging_extra = get_logging_extra(user_id)
    logging_extra["question"] = question_text

    language = await _l(user_id)

    try:
        logger.info("question for embedding", extra_data=logging_extra)

        question, answer, value = await ai_chat_service.get_related_question_from_db(question_text)  # message.from_user.id,

        # we know it's a bad answer
        if not value or isinstance(value, numpy.float64) and float(value) < bot_config.EMBEDDING_THRESHOLD:
            await unknown_question(message.chat.id, question_text)
        # we let user say if he likes it
        else:
            answer_message = await message.answer(text=f"{question}\n\n{answer}",
                                                reply_markup=ai_response_keyboard("", language))
            answer_message_id = answer_message.message_id

            # call after new answer
            asyncio.create_task(new_answer_message(user_id, question_text, answer_message_id, state))

    except Exception as e:
        logger.error("error while embedding", exc_info=e, extra_data=logging_extra)

        await message.answer(_("Не удалось получить ответ на вопрос", language))


@router.callback_query(F.data.startswith("bad_answer_"))
async def bad_answer_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logging_extra = get_logging_extra(user_id)

    question_text = await state.get_value("question_text", None)

    # whoops
    if question_text is None:
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    question_text = str(question_text)

    current_state = await state.get_state()
    already_in_ai_chat = current_state == States.ai_chat.state
    print(current_state, States.ai_chat.state, already_in_ai_chat)

    await unknown_question(callback.message.chat.id, question_text, be_silent=already_in_ai_chat)

    logging_extra["question"] = question_text

    logger.info("click bad answer", extra_data=logging_extra)

    if already_in_ai_chat:
        await state.set_state(States.ai_chat)
        await ask_chat_bot(user_id, question_text, logging_extra, state)


@router.callback_query(F.data.startswith("ask_ai"))
async def ask_ai_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await _l(user_id)
    logging_extra = get_logging_extra(user_id)

    await state.set_state(States.ai_chat)
    logger.info("called for chat bot", extra_data=logging_extra)

    await callback.message.answer(_("Задайте свой вопрос", language))


@router.message(States.ai_chat)
async def ai_chat_bot_message_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logging_extra = get_logging_extra(user_id)
    question_text = message.text

    logging_extra["question"] = question_text

    logger.info("asked chat bot", extra_data=logging_extra)

    await ask_chat_bot(user_id, question_text, logging_extra, state)
