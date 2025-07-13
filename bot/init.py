from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from bot_structure_dict import bot_structure
from db.session import create_sqlalchemy_sessionmaker
from db.utils import get_asyncpg_url
from redis_conn import get_redis_url
from config import BotConfig
from services.category_service.repositories.in_dict import CategoryRepositoryInDict
from services.category_service.service import CategoryService
from services.user_service.repositories.postgres import UserRepositoryPostgres
from services.user_service.service import UserService

bot_config = BotConfig()

postgres_url = get_asyncpg_url(
    bot_config.POSTGRES_USER,
    bot_config.POSTGRES_PASSWORD,
    bot_config.POSTGRES_HOST,
    bot_config.POSTGRES_PORT,
    bot_config.POSTGRES_DB,
)
redis_url = get_redis_url(
    bot_config.REDIS_USER,
    bot_config.REDIS_PASSWORD,
    bot_config.REDIS_HOST,
    bot_config.REDIS_PORT,
    bot_config.REDIS_DB_FOR_DP,
)

postgres_conn = create_sqlalchemy_sessionmaker(
    url=postgres_url,
)

users_repo = UserRepositoryPostgres(postgres_conn)
users_service = UserService(users_repo)

category_repo = CategoryRepositoryInDict(bot_structure)
category_service = CategoryService(category_repo)

bot = Bot(token=bot_config.API_TOKEN)
dp = Dispatcher(storage=RedisStorage.from_url(redis_url))