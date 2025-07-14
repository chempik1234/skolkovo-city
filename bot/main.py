import asyncio

from init import bot, dp
from handlers import routers_list
from commands import router as commands_router

dp.include_routers(commands_router, *routers_list)


async def start():
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start())
