import asyncio

from init import bot, dp
from routers import routers_list
from commands import router as commands_router
from middlewares.check_registration_middleware import CheckRegistrationMiddleware

dp.include_routers(commands_router, *routers_list)
dp.update.outer_middleware(CheckRegistrationMiddleware())


async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def start():
    await asyncio.gather(start_bot())


if __name__ == "__main__":
    asyncio.run(start())
