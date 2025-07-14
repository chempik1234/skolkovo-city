from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from bot_structure_dict import bot_structure
from db.session import create_sqlalchemy_sessionmaker
from db.utils import get_asyncpg_url
from init_configs import postgres_url, bot_config, redis_url
from redis_conn import get_redis_url
from config import BotConfig
from services.category_service.repositories.in_dict import CategoryRepositoryInDict
from services.category_service.repositories.postgres import CategoryRepositoryPostgres
from services.category_service.service import CategoryService
from services.user_service.repositories.postgres import UserRepositoryPostgres
from services.user_service.service import UserService

postgres_conn = create_sqlalchemy_sessionmaker(
    url=postgres_url,
)

users_repo = UserRepositoryPostgres(postgres_conn)
users_service = UserService(users_repo)

category_repo = CategoryRepositoryPostgres(postgres_conn)
category_service = CategoryService(category_repo)

bot = Bot(token=bot_config.API_TOKEN)
dp = Dispatcher(storage=RedisStorage.from_url(redis_url))
