# part of it was made by donBarbos https://github.com/donBarbos/telegram-bot-template
import asyncio
import logging

from init import bot, dp, app, reloader_service, news_repo
from handlers import routers_list
from commands import router as commands_router
from init_configs import bot_config
from middlewares.check_registration_middleware import CheckRegistrationMiddleware
from middlewares.prometheus import prometheus_middleware_factory
from start_bot import start_bot
from web.metrics import MetricsView

logger = logging.getLogger('main')


async def on_startup() -> None:
    logger.info("bot startup beginning")
    asyncio.create_task(reloader_service.run_forever())
    asyncio.create_task(news_repo.connect())  # just to send messages

    dp.include_routers(commands_router, *routers_list)
    dp.message.outer_middleware(CheckRegistrationMiddleware())
    dp.callback_query.outer_middleware(CheckRegistrationMiddleware())

    if bot_config.BOT_USE_WEBHOOK:
        app.middlewares.append(prometheus_middleware_factory())
        app.router.add_route("GET", "/metrics", MetricsView)
    logger.info("bot startup configured")


async def on_shutdown() -> None:
    logger.info("bot shutdown")
    await reloader_service.stop()
    await bot.delete_webhook()
    await bot.session.close()


async def start():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("starting bot")
    await start_bot(bot, dp, app)


if __name__ == "__main__":
    asyncio.run(start())
