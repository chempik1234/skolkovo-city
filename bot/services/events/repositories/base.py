class EventsRepositoryBase:
    async def get_events_list(self, start_date: str, page: int, size: int):
        raise NotImplementedError()
