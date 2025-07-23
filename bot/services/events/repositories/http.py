import requests

from config import BotConfig
from services.events.repositories.base import EventsRepositoryBase


class EventsRepositoryHTTP(EventsRepositoryBase):
    def __init__(self, url: str):
        self.url = url

    async def get_events_list(self, start_date: str, page: int, all_: int = 0):
        params = {
            "StartDate": start_date,
            "page": page,
            "all": all_
        }
        response = requests.get(self.url, params=params)
        result = response.json()
        result["data"] = result["data"][: 2]
        return result
