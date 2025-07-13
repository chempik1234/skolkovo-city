from aiogram import BaseMiddleware


class CheckRegistrationMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        result = await handler(event, data)  # send to register if no data

        return result
