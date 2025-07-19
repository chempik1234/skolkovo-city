import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp.web_app import Application
from aiohttp.web_runner import AppRunner, TCPSite

from init_configs import bot_config

logger = logging.getLogger("start_bot")


async def start_bot(bot: Bot, dp: Dispatcher, app: Application, only_handled_updates=True):
    logger.info("starting bot")
    update_types = dp.resolve_used_update_types() if only_handled_updates else None
    if bot_config.BOT_USE_WEBHOOK:
        logger.info("using webhook")
        startup_exception = None
        for i in range(5):
            try:
                logger.info("connecting to webhook...")
                await bot.set_webhook(
                    url=bot_config.BOT_WEBHOOK_URL,
                    allowed_updates=update_types,
                    secret_token=bot_config.WEBHOOK_SECRET,
                )
                startup_exception = None
                logger.info("webhook connection established")
                break
            except Exception as e:
                startup_exception = e
                logger.warning("webhook connection error, retrying")
                await asyncio.sleep(2)
        if startup_exception:
            logging.critical("webhook connection", exc_info=startup_exception)
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

        logger.info("start bot successful: webhook")

        await asyncio.Event().wait()
    else:
        logger.info("starting bot polling")
        await dp.start_polling(bot, allowed_updates=update_types)