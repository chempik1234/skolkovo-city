from config import BotConfig
from db.utils import get_asyncpg_url
from redis_conn import get_redis_url

bot_config = BotConfig()

postgres_url = get_asyncpg_url(
    bot_config.POSTGRES_USER,
    bot_config.POSTGRES_PASSWORD,
    bot_config.POSTGRES_HOST,
    bot_config.POSTGRES_PORT,
    bot_config.POSTGRES_DB,
)
postgres_url_alembic = (postgres_url.replace("+asyncpg", "").
                        replace(f"@{bot_config.POSTGRES_HOST}", "@localhost"))
redis_url = get_redis_url(
    bot_config.REDIS_USER,
    bot_config.REDIS_PASSWORD,
    bot_config.REDIS_HOST,
    bot_config.REDIS_PORT,
    bot_config.REDIS_DB_FOR_DP,
)
