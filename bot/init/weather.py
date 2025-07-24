from init.init_0 import bot_config
from init.init_1 import redis_conn_users
from services.weather_service.repositories.cache.redis import WeatherCacheRepositoryRedis
from services.weather_service.repositories.weather.openweathermap import WeatherRepositoryOpenWeatherMap
from services.weather_service.service import WeatherService
from utils import get_seconds_till_next_weather

weather_repositories = [
    WeatherRepositoryOpenWeatherMap(bot_config.OPENWEATHERMAP_URL,
                                    lat=bot_config.OPENWEATHERMAP_LAT,
                                    lon=bot_config.OPENWEATHERMAP_LON,
                                    api_key=bot_config.OPENWEATHERMAP_API_KEY),
]
weather_cache_repo = WeatherCacheRepositoryRedis(redis_conn_users, get_seconds_till_next_weather)
weather_service = WeatherService(weather_repositories, cache_repo=weather_cache_repo)