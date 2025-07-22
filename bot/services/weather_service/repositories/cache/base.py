class WeatherCacheRepositoryBase:
    async def get_text(self, language) -> str | None:
        raise NotImplementedError()

    async def set_text(self, language, text) -> None:
        raise NotImplementedError()
