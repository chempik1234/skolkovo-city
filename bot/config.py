import os

from aiogram.fsm.state import StatesGroup, State
from betterconf import Config
from betterconf.config import Field
from dotenv import load_dotenv

load_dotenv("../config/.env", override=True)


class BotConfig(Config):
    API_TOKEN: str = Field("API_TOKEN")
    WEBHOOK_SECRET: str = Field("WEBHOOK_SECRET", default="1234")

    #region redis conf
    REDIS_HOST: str = Field("REDIS_HOST")
    REDIS_PORT: int = Field("REDIS_PORT", default="6379")
    REDIS_DB_FOR_DP: int = Field("REDIS_DB_FOR_DP", default="0")
    REDIS_DB_FOR_USERS: int = Field("REDIS_DB_FOR_USERS", default="1")
    REDIS_USER: str = Field("REDIS_USER", default="default")
    REDIS_PASSWORD: str = Field("REDIS_PASSWORD")
    REDIS_USERS_EXPIRE_SECONDS: int = Field("REDIS_USERS_EXPIRE_SECONDS", default=600)
    #endregion

    #region postgres conf
    POSTGRES_DB: str = Field("POSTGRES_DB")
    POSTGRES_HOST: str = Field("POSTGRES_HOST", default="db")
    POSTGRES_USER: str = Field("POSTGRES_USER", default="postgres")
    POSTGRES_PASSWORD: str = Field("POSTGRES_PASSWORD")
    POSTGRES_PORT: int = Field("POSTGRES_PORT", default="5432")
    #endregion

    BOT_ROOT_CATEGORY_STR: str = Field("BOT_ROOT_CATEGORY", "None")
    BOT_WEBHOOK_HOST: str = Field("BOT_WEBHOOK_HOST", default="0.0.0.0")
    BOT_WEBHOOK_BASE: str = Field("BOT_WEBHOOK_BASE", default="")
    BOT_WEBHOOK_PORT: int = Field("BOT_WEBHOOK_PORT", default="5000")
    BOT_WEBHOOK_PATH: str = Field("BOT_WEBHOOK_PATH", default="/webhook")

    _BOT_USE_WEBHOOK: bool = Field("BOT_USE_WEBHOOK")

    @property
    def BOT_WEBHOOK_URL(self):
        return f"https://{self.BOT_WEBHOOK_BASE}{self.BOT_WEBHOOK_PATH}"

    @property
    def BOT_USE_WEBHOOK(self):
        return self._BOT_USE_WEBHOOK == "True"

    @property
    def USE_PROMETHEUS(self):
        return self.BOT_USE_WEBHOOK


class States(StatesGroup):
    default = State()
    category = State()


# class RegistrationStates(StatesGroup):
#     full_name = State()
#     email = State()
#     agreement = State()
