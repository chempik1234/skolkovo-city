import asyncio

import structlog

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot_functions.category import handle_category
from bot_functions.settings import make_user_choose_language
from config import NewsForm, States
from init import category_service, users_service, reloader_service
from init.ai_chat_service import ai_chat_service
from init.init_0 import BOT_ROOT_CATEGORY
from keyboards import yes_no_keyboard
from utils import get_logging_extra

logger = structlog.get_logger(name="commands")

router = Router()


@router.message(Command(commands=["start"]))
async def command_start(message: Message, state: FSMContext):
    logging_extra = get_logging_extra(message.from_user.id)
    try:
        logger.info("/start command", extra_data=logging_extra)
        await handle_category(current_category_id=BOT_ROOT_CATEGORY, chat_id=message.chat.id,
                              category_message=None, state=state)
        await state.set_state(States.default)
    except Exception as e:
        logger.error("error while trying to /start", extra_data=logging_extra, exc_info=e)


@router.message(Command(commands=["language"]))
async def command_settings(message: Message, state: FSMContext):
    logging_extra = get_logging_extra(message.from_user.id)
    logger.info("/language command", extra_data=logging_extra)
    await make_user_choose_language(user_id=message.from_user.id)


@router.message(Command(commands=["reload"]))
async def command_reload(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logging_extra = get_logging_extra(user_id)

    logger.info("/reload command", extra_data=logging_extra)

    try:
        is_admin = await users_service.is_admin(user_id)
    except Exception as e:
        logger.error("error while trying to /reload", extra_data=logging_extra, exc_info=e)
        return

    if is_admin:
        await message.answer(text="Структура ботов перезагружается, подождите")

        logger.info("sending to reload", extra_data=logging_extra)

        try:
            await reloader_service.reload_instances()

            logger.info("reloading is queued", extra_data=logging_extra)

            await message.answer(text="Запрос на перезагрузку отправлен в очередь")
        except Exception as e:
            logger.error("error while /reload", extra_data=logging_extra, exc_info=e)
    else:
        logger.warning("someone tried to use /reload", extra_data=logging_extra)


@router.message(Command(commands=["news"]))
async def command_news(message: Message, state: FSMContext):
    user_id = message.from_user.id

    logging_extra = get_logging_extra(user_id)
    
    try:
        is_admin = await users_service.is_admin(user_id)
    except Exception as e:
        logger.error("error while trying to /news", extra_data=logging_extra, exc_info=e)
        return

    if is_admin:
        logger.info("/news command by admin", extra_data=logging_extra)
        await message.answer(
            "📢 Отправьте сообщение для рассылки (текст, фото, видео, gif):"
        )
        await state.set_state(NewsForm.waiting_for_content)


@router.message(Command(commands=["search_index_upload"]))
async def command_reload(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logging_extra = get_logging_extra(user_id)

    logger.info("/search_index_upload command", extra_data=logging_extra)

    try:
        is_admin = await users_service.is_admin(user_id)
    except Exception as e:
        logger.error("error while trying to /search_index_upload", extra_data=logging_extra, exc_info=e)
        return

    if is_admin:
        await state.set_state(States.ai_upload_index_confirmation)
        await message.answer(
            "🚨🚨🚨 Опасно!\n\nЭто дорогая операция (не меньше 500₽)! Вы точно уверены?",
            reply_markup=yes_no_keyboard,
        )


@router.message(Command(commands=["search_index_delete_all"]))
async def command_delete_all_search_indexes(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logging_extra = get_logging_extra(user_id)

    logger.info("/search_index_upload command", extra_data=logging_extra)

    try:
        is_admin = await users_service.is_admin(user_id)
    except Exception as e:
        logger.error("error while trying to /search_index_upload", extra_data=logging_extra, exc_info=e)
        return

    if is_admin:
        await state.set_state(States.ai_delete_indexes_confirmation)
        await message.answer(
            "🚨🚨🚨 Опасно!\n\n Бот больше не сможет искать какую-либо информацию о сколково, а вернуть индексы -"
            " дорогая операция (не меньше 500₽)! Вы точно уверены?",
            reply_markup=yes_no_keyboard,
        )
