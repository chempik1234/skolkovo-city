import structlog

import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiohttp import web

from db.session import create_sqlalchemy_sessionmaker
from init_configs import postgres_url, bot_config, redis_url_dp, redis_url_users, rabbitmq_url
from redis_conn import create_redis
from services.category_service.repositories.postgres import CategoryRepositoryPostgres
from services.category_service.service import CategoryService
from services.news_service.repositories.rabbitmq import NewsSenderRepositoryRabbitMQ
from services.news_service.service import NewsSenderService
from services.reloader_service.repositories.rabbitmq import ReloaderRepositoryRabbitMQ
from services.reloader_service.service import ReloaderService
from services.user_service.repositories.cache.redis_repo import UserCacheRepositoryRedis
from services.user_service.repositories.storage.postgres import UserStorageRepositoryPostgres
from services.user_service.service import UserService
from services.weather_service.repositories.openweathermap import WeatherRepositoryOpenWeatherMap

from services.weather_service.repositories.cache.redis import WeatherCacheRepositoryRedis
from services.weather_service.service import WeatherService
from utils import get_seconds_till_next_weather

postgres_conn = create_sqlalchemy_sessionmaker(
    url=postgres_url,
)
redis_conn_dp = RedisStorage.from_url(redis_url_dp)
redis_conn_users = create_redis(bot_config.REDIS_HOST, bot_config.REDIS_PORT,
                                bot_config.REDIS_DB_FOR_USERS, bot_config.REDIS_PASSWORD)
    # pika.ConnectionParameters(
    #     host=bot_config.RABBITMQ_HOST,
    #     port=bot_config.RABBITMQ_PORT,
    #     virtual_host=bot_config.RABBITMQ_VIRTUAL_HOST,
    #     credentials=pika.PlainCredentials(
    #         username=bot_config.RABBITMQ_USER,
    #         password=bot_config.RABBITMQ_PASSWORD,
    #     ),
    #     heartbeat=bot_config.RABBITMQ_HEARTBEAT,
    # ),

weather_repositories = [
    WeatherRepositoryOpenWeatherMap(bot_config.OPENWEATHERMAP_URL,
                                    lat=bot_config.OPENWEATHERMAP_LAT,
                                    lon=bot_config.OPENWEATHERMAP_LON,
                                    api_key=bot_config.OPENWEATHERMAP_API_KEY),
]
weather_cache_repo = WeatherCacheRepositoryRedis(redis_conn_users, get_seconds_till_next_weather)
weather_service = WeatherService(weather_repositories, cache_repo=weather_cache_repo)

users_storage_repo = UserStorageRepositoryPostgres(postgres_conn)
users_cache_repo = UserCacheRepositoryRedis(redis_conn_users, lambda: bot_config.REDIS_USERS_EXPIRE_SECONDS)
users_service = UserService(users_storage_repo, users_cache_repo)

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
