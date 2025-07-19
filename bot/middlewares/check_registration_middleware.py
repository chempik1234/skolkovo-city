import logging

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from bot_functions.settings import make_user_choose_language
from bot_functions.user import check_user_data

logger = logging.getLogger("check_registration_middleware")


class CheckRegistrationMiddleware(BaseMiddleware):
    async def __call__(self, handler: Message | CallbackQuery, event, data):
        user_id, passed, created_new_user = None, True, False
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id:
            try:
                passed, created_new_user = await check_user_data(user_id)
            except Exception as e:
                logger.error("error while checking user data", extra={"user_id": user_id}, exc_info=e)
                return

        if created_new_user:
            logger.info("created new user", extra={"user_id": user_id})
            await make_user_choose_language(user_id)
        elif passed:
            result = await handler(event, data)
            return result
