import asyncio

from init import bot, dp
from handlers import routers_list
from commands import router as commands_router
from middlewares.check_registration_middleware import CheckRegistrationMiddleware

dp.include_routers(commands_router, *routers_list)
dp.message.outer_middleware(CheckRegistrationMiddleware())
dp.callback_query.outer_middleware(CheckRegistrationMiddleware())


async def start():
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start())
