from custom_types import Language


class WeatherRepositoryBase:
    async def get_weather_text(self, language: Language) -> str:
        raise NotImplementedError()

    async def get_weather_raw(self) -> str:
        raise NotImplementedError()
