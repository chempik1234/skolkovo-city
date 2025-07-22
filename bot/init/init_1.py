from aiogram.fsm.storage.redis import RedisStorage

from db.session import create_sqlalchemy_sessionmaker
from .init_0 import postgres_url, bot_config, redis_url_dp
from redis_conn import create_redis
from services.user_service.repositories.cache.redis_repo import UserCacheRepositoryRedis
from services.user_service.repositories.storage.postgres import UserStorageRepositoryPostgres
from services.user_service.service import UserService

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

users_storage_repo = UserStorageRepositoryPostgres(postgres_conn)
users_cache_repo = UserCacheRepositoryRedis(redis_conn_users, lambda: bot_config.REDIS_USERS_EXPIRE_SECONDS)
users_service = UserService(users_storage_repo, users_cache_repo)