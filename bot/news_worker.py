# part of it was made by donBarbos https://github.com/donBarbos/telegram-bot-template
import asyncio

from init import bot, app, news_service, create_dp
from init_configs import bot_config
from middlewares.prometheus import prometheus_middleware_factory
from start_bot import start_bot
from web.metrics import MetricsView


async def on_startup() -> None:
    if bot_config.BOT_USE_WEBHOOK:
        app.middlewares.append(prometheus_middleware_factory())
        app.router.add_route("GET", "/metrics", MetricsView)


async def on_shutdown() -> None:
    await bot.delete_webhook()
    await bot.session.close()


async def start():
    light_dp = create_dp()
    light_dp.startup.register(on_startup)
    light_dp.shutdown.register(on_shutdown)

    @light_dp.message()
    async def handler(message) -> None:
        await message.answer("критическая ошибка проксирования!")

    asyncio.create_task(start_bot(bot, light_dp, app, only_handled_updates=False))
    async for message in news_service.read():
        telegram_id = message["telegram_id"]
        content = message["content"]
        text = content["text"]
        caption = content["caption"]
        photo = content["photo"]
        video = content["video"]
        animation = content["animation"]
        if not photo and not video and not animation:
            await bot.send_message(telegram_id, text)
        elif photo:
            await bot.send_photo(telegram_id, photo, caption=caption)
        elif video:
            await bot.send_video(telegram_id, video, caption=caption)
        elif animation:
            await bot.send_animation(telegram_id, animation)


if __name__ == "__main__":
    asyncio.run(start())
