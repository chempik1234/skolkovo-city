from datetime import datetime
from typing import Callable

from redis import Redis
from services.rate_limiter.repositories.base import RateLimiterRepositoryBase, RateLimiterException
from services.redis_mixin import RedisMixin


class RateLimiterRepositoryRedisFixedWindow(RedisMixin, RateLimiterRepositoryBase):
    def __init__(self, redis: Redis, window_period_seconds: int, max_counter_value: int):
        super().__init__(redis, lambda: window_period_seconds)  # only by default if window_start value is None

        self.window_period_seconds = window_period_seconds
        self.max_counter_value = max_counter_value

    def _key_counter(self, telegram_id: int | str, name: str) -> str:
        return f"rate__limiter__counter__{name}__{telegram_id}"

    def _key_window_start(self, telegram_id: int | str, name: str) -> str:
        return f"rate__limiter__window__{name}__{telegram_id}"

    async def can_user_do_action(self, telegram_id: int | str, name: str) -> bool:
        counter_value = self.get(self._key_counter(telegram_id, name))
        if counter_value is None:
            return True
        counter_value = int(counter_value)
        return counter_value < self.max_counter_value

    async def increase_counter(self, telegram_id: int | str, name: str) -> None:
        if not await self.can_user_do_action(telegram_id, name):
            raise RateLimiterException()

        counter_value = self.get(self._key_counter(telegram_id, name))
        if counter_value is None:
            self.set(self._key_counter(telegram_id, name), 1)  # expires in WINDOW_PERIOD
            self.set(self._key_window_start(telegram_id, name), str(datetime.timestamp(datetime.now())))
            return
        counter_value = int(counter_value)

        # 1. get when does window end
        # ---|+1 +1 +1 +1       |------------|+1  +1    +1 +1     +1  |---|+1                   |
        #                     window       first_inc               window                    window
        #                ========                                   ==       ===================
        #              the time we get                              the time we get
        window_start = self.get(self._key_window_start(telegram_id, name))
        if window_start is None:
            time_till_window_end = self.window_period_seconds
        else:
            window_start = float(window_start)
            time_till_window_end = int(window_start + self.window_period_seconds - datetime.timestamp(datetime.now()))

        self.set(self._key_counter(telegram_id, name), counter_value + 1, ex=time_till_window_end)
