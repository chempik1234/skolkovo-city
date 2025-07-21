import asyncio

import structlog
import uuid

from aiogram import Router, F
from aiogram.enums import ReactionTypeType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReactionTypeEmoji

from config import NewsForm, States
from init import news_service, users_service
from utils import get_logging_extra

logger = structlog.get_logger(name="handlers.news")

router = Router()


@router.message(NewsForm.waiting_for_content)
async def process_news_content(message: Message, state: FSMContext):
    logging_extra = get_logging_extra(message.from_user.id)

    logger.info("someone trying to send news", extra_data=logging_extra)

    await message.answer("Подождите немного, сейчас начнётся...")

    if message.media_group_id is not None:
        # handle only after last message
        logger.info("receiving media_group message", extra_data=logging_extra)

        # 1. add current message
        current_media_group = await state.get_value("current_media_group", [])
        if not isinstance(current_media_group, list):
            current_media_group = []

        message_json = news_service.serialize_message_json(message)
        current_media_group.append(message_json)

        # 2. if it changed then there were another messages, return
        current_media_group_len = len(current_media_group)

        await state.update_data({"current_media_group": current_media_group})

        await asyncio.sleep(2)  # per message, not the whole group

        current_media_group = await state.get_value("current_media_group", [])
        if len(current_media_group) != current_media_group_len:
            return

        # No new messages, it's our turn
        await state.update_data({"current_media_group": None})

        what_to_send = current_media_group
    else:
        # Handling single message is quite easy
        what_to_send = message

    logger.info("begging the mailing", extra_data=logging_extra)
    await news_service.send(what_to_send, await users_service.get_objects_field("telegram_id"))
    logger.info("mailing started", extra_data=logging_extra)

    await message.answer("✅ Контент принят. Рассылка начата в фоновом режиме.")
    await state.set_state(States.default)