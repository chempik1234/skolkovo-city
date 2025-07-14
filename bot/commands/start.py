import asyncio
import time

from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot_functions.category import handle_category
from bot_functions.user import check_user_data
from init import category_service, users_service
from .commands_router import router


@router.message(Command(commands=["start"]))
async def command_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if await check_user_data(user_id, state):  # returns True if user filled his data, else sends form
        await handle_category(current_category_id=None, chat_id=message.chat.id,
                              category_message=None, state=state)


@router.message(Command(commands=["reload"]))
async def command_reload(message: Message, state: FSMContext):
    await message.answer(text=f"Структура ботов начинает перезагружаться, подождите")
    start_time = time.time()
    category_service.reload_categories()
    end_time = time.time()
    await message.answer(text=f"Структура ботов перезагружена {round(end_time - start_time, 4)}с")
