import requests

from config import BotConfig
from services.events.repositories.base import EventsRepositoryBase


class EventsRepositoryHTTP(EventsRepositoryBase):
    def __init__(self, url: str):
        self.url = url

    async def get_events_list(self, start_date: str, page: int, size: int):
        params = {
            "StartDate": start_date,
            "page": page,
            "size": size
        }
        response = requests.get(self.url, params=params)
        result = response.json()
        result["data"] = result["data"]
        return result
