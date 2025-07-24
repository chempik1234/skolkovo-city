import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

from .init_1 import redis_conn_users, postgres_conn, redis_conn_dp, users_service
from .ai_chat_service import ai_chat_service
from .weather import weather_service
from .init_0 import bot_config, rabbitmq_url
from services.category_service.repositories.postgres import CategoryRepositoryPostgres
from services.category_service.service import CategoryService
from services.news_service.repositories.rabbitmq import NewsSenderRepositoryRabbitMQ
from services.news_service.service import NewsSenderService
from services.reloader_service.repositories.rabbitmq import ReloaderRepositoryRabbitMQ
from services.reloader_service.service import ReloaderService


category_repo = CategoryRepositoryPostgres(postgres_conn)
category_service = CategoryService(category_repo)

reloader_repo = ReloaderRepositoryRabbitMQ(rabbitmq_url, "reloading")
reloader_service = ReloaderService(reloader_repo, category_service.reload_categories)

news_repo = NewsSenderRepositoryRabbitMQ(rabbitmq_url, "news")
news_service = NewsSenderService(news_repo)

bot = Bot(token=bot_config.API_TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
app = web.Application()


def create_dp() -> Dispatcher:
    return Dispatcher(storage=redis_conn_dp)


dp = create_dp()

structlog.configure(
    processors=[
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer()
    ]
)
