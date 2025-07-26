import asyncio
from typing import Tuple

import numpy
import structlog
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot_functions.category import send_category
from custom_types import Language, LanguageEnum
from init import bot, category_service
from init.ai_chat_service import ai_chat_service
from init.init_0 import bot_config
from keyboards import ai_response_keyboard
from models.ai_chat import Question
from retry import retry_async_generator
from services.rate_limiter.repositories.base import RateLimiterException
from utils import get_logging_extra, split_text_for_telegram
from translation import get_language_for_telegram_id as _l, translate_string as _

logger = structlog.get_logger(__name__)


async def _ask_embedding(
        question_text: str,
        language: Language =
        LanguageEnum.ru
) -> Tuple[Question | None, numpy.float64 | None]:
    text_lower = question_text.lower()
    if any([i in text_lower for i in ["погод", "мероприят", "api", "сегодня", "event", "today", "current", "weath", "this"]]):
        return None, None

    found_answer = True

    question, value = await ai_chat_service.get_related_question_from_db(question_text, language,
                                                                         search_among_category=True)
    # we know bot categories don't show the full information
    if not value or isinstance(value, numpy.float64) and float(value) < bot_config.EMBEDDING_THRESHOLD:
        question, value = await ai_chat_service.get_related_question_from_db(question_text, language,
                                                                             search_among_non_category=True)
        # if there are no answers at all
        if not value or isinstance(value, numpy.float64) and float(value) < bot_config.EMBEDDING_THRESHOLD:
            found_answer = False

    if found_answer:
        return question, value
    return None, None


async def ask_chat_bot(user_id: int | str, question_text: str,
                       logging_extra: dict | None, state: FSMContext,
                       skip_embedding_mode: bool = False):
    language = await _l(user_id)
    if not logging_extra:
        logging_extra = get_logging_extra(user_id)


    wait_for_answer_message = answer_message = None
    try:
        wait_for_answer_message = await bot.send_message(chat_id=user_id, text="⏲️")

        found_answer = False
        answer, category_id = "", None  # it won't be used anyway: if no answer then exception

        if not skip_embedding_mode:
            question_object, value = await _ask_embedding(question_text, language)
            if question_object:
                answer = question_object.answer_ru if language == LanguageEnum.ru else question_object.answer_en
                category_id = question_object.category_id
                found_answer = True

        if not found_answer:
            # Try to get response from AI for 3 times
            async for retry_response in (retry_async_generator(
                    ai_chat_service.get_response,
                    tries=5,
                    function_args=(user_id, question_text),
            )):  # message.from_user.id,
                success, ai_answer = retry_response
                if success:
                    found_answer, answer = True, ai_answer
                    break
                # await bot.send_message(user_id, _("Неудачная попытка, пробуем ещё раз...", language))

        # Success, else we would be in except
        logger.info("got answer from AI Chatbot", extra_data=logging_extra)

        if category_id is None:
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
        else:
            await send_category(None, user_id, await category_service.get_object(category_id), state)
            answer_message = await bot.send_message(user_id,
                                                    text=_(bot_config.EMBEDDING_CATEGORY_MESSAGE_RU, language))
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
        asyncio.create_task(_new_answer_message(user_id, question_text, answer_message.message_id, state))


async def _new_answer_message(user_id: int | str, question_text, message_id: int | str, state: FSMContext):
    """
    call when bot sends a new answer
    """
    try:
        await _delete_ai_response_keyboards_from_state(user_id, state)
    except:  # no keyboard changes
        pass
    await state.update_data(question_text=question_text, answer_message_ids=[message_id])


async def _delete_ai_response_keyboards_from_state(user_id: int | str, state: FSMContext):
    answer_message_ids = await state.get_value("answer_message_ids", [])
    for deprecated_message_id in answer_message_ids:
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=deprecated_message_id, reply_markup=None)
