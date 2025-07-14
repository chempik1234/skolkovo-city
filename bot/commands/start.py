from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from bot_functions.category import handle_category
from .commands_router import router


@router.message(Command(commands=["start"]))
async def command_start(message, state: FSMContext):
    await handle_category(current_category_id=None, chat_id=message.chat.id,
                          category_message=None, state=state)
