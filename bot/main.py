# part of it was made by donBarbos https://github.com/donBarbos/telegram-bot-template
import asyncio
import threading

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp.web_runner import AppRunner, TCPSite

from init import bot, dp, app, reloader_service, reloader_repo
from handlers import routers_list
from commands import router as commands_router
from init_configs import bot_config
from middlewares.check_registration_middleware import CheckRegistrationMiddleware
from middlewares.prometheus import prometheus_middleware_factory
from web.metrics import MetricsView


async def on_startup() -> None:
    asyncio.create_task(reloader_service.run_forever())

    dp.include_routers(commands_router, *routers_list)
    dp.message.outer_middleware(CheckRegistrationMiddleware())
    dp.callback_query.outer_middleware(CheckRegistrationMiddleware())

    if bot_config.BOT_USE_WEBHOOK:
        app.middlewares.append(prometheus_middleware_factory())
        app.router.add_route("GET", "/metrics", MetricsView)


async def on_shutdown() -> None:
    await reloader_service.stop()
    await bot.delete_webhook()
    await bot.session.close()


async def start():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    if bot_config.BOT_USE_WEBHOOK:
        startup_exception = None
        for i in range(5):
            try:
                await bot.set_webhook(
                    url=bot_config.BOT_WEBHOOK_URL,
                    allowed_updates=dp.resolve_used_update_types(),
                    secret_token=bot_config.WEBHOOK_SECRET,
                )
                startup_exception = None
                break
            except Exception as e:
                startup_exception = e
                await asyncio.sleep(2)
        if startup_exception:
            raise startup_exception
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=bot_config.WEBHOOK_SECRET,
        )
        webhook_requests_handler.register(app, path=bot_config.BOT_WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        runner = AppRunner(app)
        await runner.setup()
        site = TCPSite(runner, host=bot_config.BOT_WEBHOOK_HOST, port=bot_config.BOT_WEBHOOK_PORT)
        await site.start()
        await asyncio.Event().wait()
    else:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(start())
