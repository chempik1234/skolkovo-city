from aiogram.fsm.state import StatesGroup, State
from betterconf import Config
from betterconf.config import Field


class BotConfig(Config):
    API_TOKEN: str = Field("API_TOKEN")

    #region redis conf
    REDIS_HOST: str = Field("REDIS_HOST")
    REDIS_PORT: int = Field("REDIS_PORT")
    REDIS_DB_FOR_DP: int = Field("REDIS_DB_FOR_DP")
    REDIS_USER: str = Field("REDIS_USER")
    REDIS_PASSWORD: str = Field("REDIS_PASSWORD")
    #endregion

    #region postgres conf
    POSTGRES_DB: str = Field("POSTGRES_DB")
    POSTGRES_HOST: str = Field("POSTGRES_HOST", default="db")
    POSTGRES_USER: str = Field("POSTGRES_USER", default="postgres")
    POSTGRES_PASSWORD: str = Field("POSTGRES_PASSWORD")
    POSTGRES_PORT: int = Field("POSTGRES_PORT", default="5432")
    #endregion


class States(StatesGroup):
    registration = State()
    """
    if field_value == "" then "please enter field value" e.g. full_name
    loop through fields and 
    """
    category = State()
