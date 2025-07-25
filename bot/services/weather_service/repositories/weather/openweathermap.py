from datetime import datetime

import requests

from services.weather_service.repositories.weather.base import WeatherRepositoryBase
from translation import translate_string as _
from custom_types import Language, LanguageEnum


class WeatherRepositoryOpenWeatherMap(WeatherRepositoryBase):
    def __init__(self, url, lat, lon, api_key):
        self.url = url
        self.lat = lat
        self.lon = lon
        self.api_key = api_key

    async def get_weather_text(self, language: Language) -> str:
        data = await self._get_service_response(language)

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        # Форматируем текст
        weather_text = (
            f"{_("Погода", language)}: ({datetime.today().strftime("%d.%m.%Y")})\n"
            f"🌡 {_("Температура", language)}: *{temp:.1f}°C ({_("ощущается как", language)} {feels_like:.1f}°C)*\n"
            f"☁️ {_("Состояние", language)}: *{description}*\n"
            f"💧 {_("Влажность", language)}: *{humidity}%*\n"
            f"🌬 {_("Ветер", language)}: *{wind_speed} м/с*"
        )

        return weather_text

    async def get_weather_raw(self) -> str:
        return str(await self._get_service_response())

    async def _get_service_response(self, language: Language = LanguageEnum.ru) -> dict:
        response = requests.get(self.url, params={"lat": self.lat, "lon": self.lon, "appid": self.api_key,
                                                  "lang": language, "units": "metric"})
        response.raise_for_status()
        data = response.json()
        return data