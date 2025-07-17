from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from bot_functions.settings import make_user_choose_language
from bot_functions.user import check_user_data


class CheckRegistrationMiddleware(BaseMiddleware):
    async def __call__(self, handler: Message | CallbackQuery, event, data):
        user_id, passed, created_new_user = None, True, False
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id:
            passed, created_new_user = await check_user_data(user_id)

        if created_new_user:
            await make_user_choose_language(user_id)
        elif passed:
            result = await handler(event, data)
            return result
