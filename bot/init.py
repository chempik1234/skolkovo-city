from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from db.session import create_sqlalchemy_sessionmaker
from init_configs import postgres_url, bot_config, redis_url_dp, redis_url_users
from redis_conn import create_redis
from services.category_service.repositories.postgres import CategoryRepositoryPostgres
from services.category_service.service import CategoryService
from services.user_service.repositories.cache.redis_repo import UserCacheRepositoryRedis
from services.user_service.repositories.storage.postgres import UserStorageRepositoryPostgres
from services.user_service.service import UserService

postgres_conn = create_sqlalchemy_sessionmaker(
    url=postgres_url,
)
redis_conn_dp = RedisStorage.from_url(redis_url_dp)
redis_conn_users = create_redis(bot_config.REDIS_HOST, bot_config.REDIS_PORT,
                                bot_config.REDIS_DB_FOR_USERS, bot_config.REDIS_PASSWORD)

users_storage_repo = UserStorageRepositoryPostgres(postgres_conn)
users_cache_repo = UserCacheRepositoryRedis(redis_conn_users, bot_config.REDIS_USERS_EXPIRE_SECONDS)
users_service = UserService(users_storage_repo, users_cache_repo)

category_repo = CategoryRepositoryPostgres(postgres_conn)
category_service = CategoryService(category_repo)

bot = Bot(token=bot_config.API_TOKEN)
dp = Dispatcher(storage=redis_conn_dp)
