import asyncio
import time

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot_functions.category import handle_category
from bot_functions.settings import make_user_choose_language
from init import category_service, users_service, reloader_service
from init_configs import BOT_ROOT_CATEGORY

router = Router()


@router.message(Command(commands=["start"]))
async def command_start(message: Message, state: FSMContext):
    await handle_category(current_category_id=BOT_ROOT_CATEGORY, chat_id=message.chat.id,
                          category_message=None, state=state)


@router.message(Command(commands=["language"]))
async def command_settings(message: Message, state: FSMContext):
    await make_user_choose_language(user_id=message.from_user.id)


@router.message(Command(commands=["reload"]))
async def command_reload(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if await users_service.is_admin(user_id):
        await message.answer(text="Структура ботов перезагружается, подождите")
        await reloader_service.reload_instances()
        await message.answer(text="Запрос на перезагрузку отправлен в очередь")
