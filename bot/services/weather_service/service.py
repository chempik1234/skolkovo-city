from typing import List

import structlog

from services.weather_service.repositories.weather.base import WeatherRepositoryBase
from services.weather_service.repositories.cache.base import WeatherCacheRepositoryBase
from custom_types import Language, LanguageEnum

logger = structlog.get_logger("weather_service")


class WeatherService:
    def __init__(self, repos: List[WeatherRepositoryBase], cache_repo: WeatherCacheRepositoryBase):
        self.repos = repos
        self.cache_repo = cache_repo

    async def get_weather_raw(self) -> str | None:
        for repo in self.repos:
            try:
                text = await repo.get_weather_raw()
                if text:
                    return text
            except Exception as e:
                logger.error("exception while getting weather raw", exc_info=e)

    async def get_weather_text(self, language: Language = LanguageEnum.ru) -> str | None:
        text = await self.cache_repo.get_text(language)
        if text:
            return text

        for repo in self.repos:
            try:
                text = await repo.get_weather_text(language)
                if text:
                    logger.info("new weather text", text=text)
                    await self.cache_repo.set_text(language, text)
                    return text
            except Exception as e:
                logger.error("exception while getting weather text", exc_info=e)
        return None
