from services.events.repositories.base import EventsRepositoryBase


class EventsService:
    def __init__(self, events_repo: EventsRepositoryBase):
        self.events_repo = events_repo

    async def get_events_list(self, start_date: str, page: int, size: int):
        return await self.events_repo.get_events_list(start_date, page, size)
