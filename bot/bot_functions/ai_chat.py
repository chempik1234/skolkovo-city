import asyncio

import structlog
from aiogram.enums import parse_mode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import States
from init import bot
from init.ai_chat_service import ai_chat_service
from init.init_0 import bot_config
from keyboards import ask_ai_keyboard, ai_response_keyboard
from retry import retry_async, retry_async_generator
from services.rate_limiter.repositories.base import RateLimiterException
from translation import get_language_for_telegram_id as _l,  translate_string as _
from utils import split_text_for_telegram, get_logging_extra

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


async def ask_chat_bot(user_id: int | str, question_text: str,
                       logging_extra: dict | None, state: FSMContext):
    language = await _l(user_id)
    if not logging_extra:
        logging_extra = get_logging_extra(user_id)


    wait_for_answer_message = answer_message = None
    try:
        wait_for_answer_message = await bot.send_message(chat_id=user_id, text="⏲️")

        answer = ""  # it won't be used anyway: if no answer then exception

        # Try to get response from AI for 3 times
        async for retry_response in retry_async_generator(
                ai_chat_service.get_response,
                tries=5,
                function_args=(user_id, question_text),
        ):  # message.from_user.id,
            success, ai_answer = retry_response
            if success:
                answer = ai_answer
                break
            # await bot.send_message(user_id, _("Неудачная попытка, пробуем ещё раз...", language))

        # Success, else we would be in except
        logger.info("got answer from AI Chatbot", extra_data=logging_extra)

        async def send_answer(answer_, parse_mode_) -> Message | None:
            split_answer = split_text_for_telegram(answer_)
            for string in split_answer[: -1]:
                await bot.send_message(user_id, string, parse_mode=parse_mode_)
            if split_answer:
                return await bot.send_message(user_id, split_answer[-1], parse_mode=parse_mode_)

        try:
            answer_message = await send_answer(answer, parse_mode_="Markdown")
        except:
            answer_message = await send_answer(answer, parse_mode_=None)
        await answer_message.edit_reply_markup(reply_markup=ai_response_keyboard("", language))

        await wait_for_answer_message.delete()

        logger.info("sent answer from AI Chatbot", extra_data=logging_extra)

    except RateLimiterException:
        await bot.send_message(user_id,
                               _("Превышено максимальное количество запросов к чат-боту! Попробуйте позже", language))
    except Exception as e:
        logger.error("error while asking AI Chatbot a question", exc_info=e, extra_data={"question": question_text})
        await bot.send_message(user_id, f"{_("Не удалось получить ответ на вопрос", language)}: {question_text}")
    finally:
        if wait_for_answer_message:
            try:
                await wait_for_answer_message.delete()
            except:
                pass

    if not answer_message is None:
        # call after new answer
        asyncio.create_task(new_answer_message(user_id, question_text, answer_message.message_id, state))


async def delete_ai_response_keyboards_from_state(user_id: int | str, state: FSMContext):
    answer_message_ids = await state.get_value("answer_message_ids", [])
    for deprecated_message_id in answer_message_ids:
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=deprecated_message_id, reply_markup=None)


async def new_answer_message(user_id: int | str, question_text, message_id: int | str, state: FSMContext):
    """
    call when bot sends a new answer
    """
    try:
        await delete_ai_response_keyboards_from_state(user_id, state)
    except:  # no keyboard changes
        pass
    await state.update_data(question_text=question_text, answer_message_ids=[message_id])
