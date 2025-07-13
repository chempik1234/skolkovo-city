from aiogram.filters.command import Command

from .commands_router import router


@router.message(Command(commands=["start"]))
async def commands(message, state):
    await message.answer("hello!")
