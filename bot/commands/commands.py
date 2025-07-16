import asyncio
import time

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot_functions.category import handle_category
from bot_functions.user import check_user_data
from config import States
from init import category_service
from keyboards import language_keyboards
from translation import translate_string as _, get_language_for_telegram_id

router = Router()


@router.message(Command(commands=["start"]))
async def command_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if await check_user_data(user_id):  # , state):
        await handle_category(current_category_id=None, chat_id=message.chat.id,
                              category_message=None, state=state)


@router.message(Command(commands=["language"]))
async def command_settings(message: Message, state: FSMContext):
    await state.set_state(States.choose_language)
    language = await get_language_for_telegram_id(message.from_user.id)
    await message.answer(text=_("Выберите язык", language), reply_markup=language_keyboards)


@router.message(Command(commands=["reload"]))
async def command_reload(message: Message, state: FSMContext):
    await message.answer(text="Структура ботов начинает перезагружаться, подождите")
    start_time = time.time()
    category_service.reload_categories()
    end_time = time.time()
    await message.answer(text=f"Структура ботов перезагружена {round(end_time - start_time, 4)}с")
