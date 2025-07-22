from services.redis_mixin import RedisMixin
from services.weather_service.repositories.cache.base import WeatherCacheRepositoryBase


class WeatherCacheRepositoryRedis(WeatherCacheRepositoryBase, RedisMixin):
    async def get_text(self, language) -> str | None:
        result: str | bytes = self.get("weather__{}".format(language))
        if not result:
            return None
        return result.decode("utf-8")


    async def set_text(self, language, text) -> None:
        return self.set("weather__{}".format(language), text)
