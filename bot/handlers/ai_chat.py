import asyncio

import structlog
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot_functions.ai_chat import unknown_question
from bot_functions.ai_chat_ask import ask_chat_bot
from config import States
from init import users_service
from init.init_2 import ai_chat_service
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

    await ask_chat_bot(user_id, question_text, logging_extra, state, False)


@router.message(States.ai_chat)
async def ai_chat_message_handler(message: Message, state: FSMContext):
    question_text = message.text

    user_id = message.from_user.id
    logging_extra = get_logging_extra(user_id)
    logging_extra["question"] = question_text

    await state.set_state(States.ai_embedding)  # don't let the dialogue go on
    await ask_chat_bot(user_id, question_text, logging_extra, state, True)


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


@router.callback_query(States.ai_upload_index_confirmation)
async def ai_update_index_confirm(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logging_extra = get_logging_extra(user_id)
    logging_extra["callback"] = callback.data

    logger.info("search_index_upload command confirmation", extra_data=logging_extra)

    if callback.data == "yes":
        try:
            is_admin = await users_service.is_admin(user_id)
        except Exception as e:
            logger.error("error while trying to /search_index_upload", extra_data=logging_extra, exc_info=e)
            return

        if is_admin:
            asyncio.create_task(ai_chat_service.upload_questions_for_search())
            await callback.message.answer(
                "Задача поставлена на фоновое выполнение."
            )
    await state.set_state(States.default)
    await callback.message.delete()


@router.callback_query(States.ai_delete_indexes_confirmation)
async def ai_delete_index_confirm(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logging_extra = get_logging_extra(user_id)
    logging_extra["callback"] = callback.data

    logger.info("search_index_delete_all command confirmation", extra_data=logging_extra)

    if callback.data == "yes":
        try:
            is_admin = await users_service.is_admin(user_id)
        except Exception as e:
            logger.error("error while trying to /search_index_delete_all", extra_data=logging_extra, exc_info=e)
            return

        if is_admin:
            asyncio.create_task(ai_chat_service.upload_questions_for_search())
            await callback.message.answer(
                "Задача поставлена на фоновое выполнение."
            )
    await state.set_state(States.default)
    await callback.message.delete()


@router.message()
async def ai_chat_bot_message_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logging_extra = get_logging_extra(user_id)
    question_text = message.text

    logging_extra["question"] = question_text

    logger.info("asked chat bot from somewhere", extra_data=logging_extra)

    await ask_chat_bot(user_id, question_text, logging_extra, state)
