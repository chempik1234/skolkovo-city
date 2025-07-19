import asyncio
import logging
import time
import uuid

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot_functions.category import handle_category
from bot_functions.settings import make_user_choose_language
from config import NewsForm
from init import category_service, users_service, reloader_service
from init_configs import BOT_ROOT_CATEGORY
from utils import get_logging_extra

logger = logging.getLogger("commands")

router = Router()


@router.message(Command(commands=["start"]))
async def command_start(message: Message, state: FSMContext):
    logging_extra = get_logging_extra(message.from_user.id)
    try:
        logger.info("/start command", extra=logging_extra)
        await handle_category(current_category_id=BOT_ROOT_CATEGORY, chat_id=message.chat.id,
                              category_message=None, state=state)
    except Exception as e:
        logger.error("error while trying to /start", extra=logging_extra, exc_info=e)


@router.message(Command(commands=["language"]))
async def command_settings(message: Message, state: FSMContext):
    logging_extra = get_logging_extra(message.from_user.id)
    logger.info("/language command", extra=logging_extra)
    await make_user_choose_language(user_id=message.from_user.id)


@router.message(Command(commands=["reload"]))
async def command_reload(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logging_extra = get_logging_extra(user_id)

    logger.info("/reload command", extra=logging_extra)

    try:
        is_admin = await users_service.is_admin(user_id)
    except Exception as e:
        logger.error("error while trying to /reload", extra=logging_extra, exc_info=e)
        return

    if is_admin:
        await message.answer(text="Структура ботов перезагружается, подождите")

        logger.info("sending to reload", extra=logging_extra)

        try:
            await reloader_service.reload_instances()

            logger.info("reloading is queued", extra=logging_extra)

            await message.answer(text="Запрос на перезагрузку отправлен в очередь")
        except Exception as e:
            logger.error("error while /reload", extra=logging_extra, exc_info=e)
    else:
        logger.warning("someone tried to use /reload", extra=logging_extra)


@router.message(Command(commands=["news"]))
async def command_news(message: Message, state: FSMContext):
    user_id = message.from_user.id

    logging_extra = get_logging_extra(user_id)
    
    try:
        is_admin = await users_service.is_admin(user_id)
    except Exception as e:
        logger.error("error while trying to /news", extra=logging_extra, exc_info=e)
        return

    if is_admin:
        logger.info("/news command by admin", extra=logging_extra)
        await message.answer(
            "📢 Отправьте сообщение для рассылки (текст, фото, видео, gif):"
        )
        await state.set_state(NewsForm.waiting_for_content)