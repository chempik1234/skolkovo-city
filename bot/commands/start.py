import time

from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from bot_functions.category import handle_category
from init import category_service
from .commands_router import router


@router.message(Command(commands=["start"]))
async def command_start(message, state: FSMContext):
    await handle_category(current_category_id=None, chat_id=message.chat.id,
                          category_message=None, state=state)


@router.message(Command(commands=["reload"]))
async def command_reload(message, state: FSMContext):
    await message.answer(text=f"Структура ботов начинает перезагружаться, подождите")
    start_time = time.time()
    category_service.reload_categories()
    end_time = time.time()
    await message.answer(text=f"Структура ботов перезагружена {round(end_time - start_time, 4)}с")
