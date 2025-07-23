class EventsRepositoryBase:
    async def get_events_list(self, start_date: str, page: int, all_: int = 0):
        raise NotImplementedError()
