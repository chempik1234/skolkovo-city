from datetime import datetime

import requests

from services.weather_service.repositories.weather.base import WeatherRepositoryBase
from translation import translate_string as _


class WeatherRepositoryOpenWeatherMap(WeatherRepositoryBase):
    def __init__(self, url, lat, lon, api_key):
        self.url = url
        self.lat = lat
        self.lon = lon
        self.api_key = api_key

    async def get_weather_text(self, language: str) -> str:
        response = requests.get(self.url, params={"lat": self.lat, "lon": self.lon, "appid": self.api_key, "lang": language})
        response.raise_for_status()
        data = response.json()

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        # Форматируем текст
        weather_text = (
            f"{_("Погода", language)}: ({datetime.today().strftime("%d:%M:%y")})\n"
            f"🌡 {_("Температура", language)}: *{temp:.1f}°C ({_("ощущается как", language)} {feels_like:.1f}°C)*\n"
            f"☁️ {_("Состояние", language)}: *{description}*\n"
            f"💧 {_("Влажность", language)}: *{humidity}%*\n"
            f"🌬 {_("Ветер", language)}: *{wind_speed} м/с*"
        )

        return weather_text