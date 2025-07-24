from services.rate_limiter.repositories.base import RateLimiterRepositoryBase


class RateLimiterService:
    def __init__(self, rate_limiter_repo: RateLimiterRepositoryBase, name: str):
        """
        Rate limiter used for a certain purpose, create for each one.

        E.g. texting the bot, asking chat bot, saving new questions
        """
        self.rate_limiter_repo = rate_limiter_repo
        self.name = name

    async def can_user_do_action(self, telegram_id: int | str) -> bool:
        return await self.rate_limiter_repo.can_user_do_action(telegram_id=telegram_id, name=self.name)

    async def increase_counter(self, telegram_id: int | str) -> None:
        await self.rate_limiter_repo.increase_counter(telegram_id=telegram_id, name=self.name)
