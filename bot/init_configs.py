from config import BotConfig
from db.utils import get_asyncpg_url
from redis_conn import get_redis_url

bot_config = BotConfig()

BOT_ROOT_CATEGORY = int(bot_config.BOT_ROOT_CATEGORY_STR) if bot_config.BOT_ROOT_CATEGORY_STR != "None" else None

postgres_url = get_asyncpg_url(
    bot_config.POSTGRES_USER,
    bot_config.POSTGRES_PASSWORD,
    bot_config.POSTGRES_HOST,
    bot_config.POSTGRES_PORT,
    bot_config.POSTGRES_DB,
)
postgres_url_alembic = (postgres_url.replace("+asyncpg", "").
                        replace(f"@{bot_config.POSTGRES_HOST}", "@localhost"))
redis_url_dp = get_redis_url(
    bot_config.REDIS_USER,
    bot_config.REDIS_PASSWORD,
    bot_config.REDIS_HOST,
    bot_config.REDIS_PORT,
    bot_config.REDIS_DB_FOR_DP,
)
redis_url_users = get_redis_url(
    bot_config.REDIS_USER,
    bot_config.REDIS_PASSWORD,
    bot_config.REDIS_HOST,
    bot_config.REDIS_PORT,
    bot_config.REDIS_DB_FOR_USERS,
)
rabbitmq_url = f"amqp://{bot_config.RABBITMQ_USER}:{bot_config.RABBITMQ_PASSWORD}@{bot_config.RABBITMQ_HOST}:{bot_config.RABBITMQ_PORT}/"