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

    if message.media_group_id is not None:
        logger.info("someone tried to send media_group, declined", extra_data=logging_extra)
        await message.answer("Медиагруппы не разрешены из-за сурового API телеграм")
        await message.react([ReactionTypeEmoji(type=ReactionTypeType.EMOJI, emoji="👎")])
        return

    await message.answer("Подождите немного, сейчас начнётся...")

    logger.info("begging the mailing", extra_data=logging_extra)
    await news_service.send(message, await users_service.get_objects_field("telegram_id"))
    logger.info("mailing started", extra_data=logging_extra)

    await message.answer("✅ Контент принят. Рассылка начата в фоновом режиме.")
    await state.set_state(States.default)