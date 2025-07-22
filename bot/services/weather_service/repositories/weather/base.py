class WeatherRepositoryBase:
    async def get_weather_text(self, language: str) -> str:
        raise NotImplementedError()
