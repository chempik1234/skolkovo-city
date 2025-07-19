# part of it was made by donBarbos https://github.com/donBarbos/telegram-bot-template
import asyncio
import datetime
import logging

from init import bot, app, news_service, create_dp
from init_configs import bot_config
from middlewares.prometheus import prometheus_middleware_factory
from start_bot import start_bot
from utils import get_logging_extra
from web.metrics import MetricsView

logger = logging.getLogger("news_worker")


async def on_startup() -> None:
    logger.info("news_worker startup beginning")
    if bot_config.BOT_USE_WEBHOOK:
        app.middlewares.append(prometheus_middleware_factory())
        app.router.add_route("GET", "/metrics", MetricsView)
    logger.info("news_worker startup configured")


async def on_shutdown() -> None:
    logger.info("news_worker shutdown")
    await bot.delete_webhook()
    await bot.session.close()


async def start():
    logger.info("starting news_worker")

    light_dp = create_dp()
    light_dp.startup.register(on_startup)
    light_dp.shutdown.register(on_shutdown)

    @light_dp.message()
    async def handler(message) -> None:
        logging.critical("bot queries are routed to worker! "
                         "check the webhook params, proxy configuration or docker port aliasing")
        await message.answer("критическая ошибка проксирования!")

    asyncio.create_task(start_bot(bot, light_dp, app, only_handled_updates=False))
    async for message in news_service.read():
        message_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

        logging_extra = get_logging_extra(None)
        logging_extra["message_id"] = str(message_id)

        _extra_with_message = logging_extra.copy()
        _extra_with_message["message"] = str(message)

        logger.debug("new message received", extra=_extra_with_message)
        try:
            telegram_id = message["telegram_id"]
            content = message["content"]
            text = content["text"]
            caption = content["caption"]
            photo = content["photo"]
            video = content["video"]
            animation = content["animation"]
            if not photo and not video and not animation:
                logger.info("- recognized as pure text", extra=logging_extra)
                await bot.send_message(telegram_id, text)
            elif photo:
                logger.info("- recognized as photo", extra=logging_extra)
                await bot.send_photo(telegram_id, photo, caption=caption)
            elif video:
                logger.info("- recognized as video", extra=logging_extra)
                await bot.send_video(telegram_id, video, caption=caption)
            elif animation:
                logger.info("- recognized as animation", extra=logging_extra)
                await bot.send_animation(telegram_id, animation)
            logger.info("- message sent", extra=logging_extra)
        except Exception as e:
            logger.error("- exception while processing message", extra=logging_extra, exc_info=e)


if __name__ == "__main__":
    asyncio.run(start())
