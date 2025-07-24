class RateLimiterRepositoryBase:
    async def can_user_do_action(self, telegram_id: int | str, name: str) -> bool:
        raise NotImplementedError()

    async def increase_counter(self, telegram_id: int | str, name: str) -> None:
        raise NotImplementedError()


class RateLimiterException(Exception):
    pass
