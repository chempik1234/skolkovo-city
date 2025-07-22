# part of it was made by donBarbos https://github.com/donBarbos/telegram-bot-template
import asyncio
import datetime
from typing import Tuple

import structlog
from aiogram.enums import InputMediaType
from aiogram.types import InputMediaPhoto, InputMediaVideo

from init import bot, app, news_service, create_dp
from init.init_0 import bot_config
from middlewares.prometheus import prometheus_middleware_factory
from start_bot import start_bot
from utils import get_logging_extra
from web.metrics import MetricsView

logger = structlog.get_logger(name="news_worker")


def get_media_type_and_media(message: dict) -> Tuple[InputMediaType | None, str | None]:
    photo = message["photo"]
    video = message["video"]
    animation = message["animation"]
    if photo:
        return InputMediaType.PHOTO, photo
    elif video:
        return InputMediaType.VIDEO, video
    elif animation:
        return InputMediaType.ANIMATION, animation
    return None, None


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
        logger.critical("bot queries are routed to worker! "
                        "check the webhook params, proxy configuration or docker port aliasing")
        await message.answer("критическая ошибка проксирования!")

    asyncio.create_task(start_bot(bot, light_dp, app, only_handled_updates=False))
    async for message in news_service.read():
        message_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

        logging_extra = get_logging_extra(None)
        logging_extra["message_id"] = str(message_id)

        _extra_with_message = logging_extra.copy()
        _extra_with_message["rabbitmq_message"] = str(message)

        logger.debug("new message received", extra_data=_extra_with_message)
        try:
            telegram_id = message["telegram_id"]
            content = message["content"]

            if isinstance(content, dict):
                text = content["text"]
                caption = content["caption"]
                photo = content["photo"]
                video = content["video"]
                animation = content["animation"]
                if not photo and not video and not animation:
                    logger.info("- recognized as pure text", extra_data=logging_extra)
                    await bot.send_message(telegram_id, text)
                elif photo:
                    logger.info("- recognized as photo", extra_data=logging_extra)
                    await bot.send_photo(telegram_id, photo, caption=caption)
                elif video:
                    logger.info("- recognized as video", extra_data=logging_extra)
                    await bot.send_video(telegram_id, video, caption=caption)
                elif animation:
                    logger.info("- recognized as animation", extra_data=logging_extra)
                    await bot.send_animation(telegram_id, animation)
            elif isinstance(content, list):
                media_group = []
                for message_part in content:
                    caption = message_part["caption"]
                    media_type, media = get_media_type_and_media(message_part)
                    if media_type == InputMediaType.PHOTO:
                        media_group.append(InputMediaPhoto(media=media, caption=caption))
                    elif media_type == InputMediaType.VIDEO:
                        media_group.append(InputMediaVideo(media=media, caption=caption))
                await bot.send_media_group(chat_id=telegram_id, media=media_group)

            logger.info("- message sent", extra_data=logging_extra)
        except Exception as e:
            logger.error("- exception while processing message", extra_data=_extra_with_message, exc_info=e)


if __name__ == "__main__":
    asyncio.run(start())
