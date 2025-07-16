from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from bot_functions.user import check_user_data


class CheckRegistrationMiddleware(BaseMiddleware):
    async def __call__(self, handler: Message | CallbackQuery, event, data):
        user_id, passed = None, True
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id:
            passed = await check_user_data(user_id)
        if passed:
            result = handler(event, data)  # send to register if no data
            return result
