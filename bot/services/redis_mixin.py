import json
from typing import Any, Callable

from redis import Redis
from sqlalchemy.orm import Mapped

from db.models import UserDataModel
from services.user_service.repositories.cache.base import UserCacheRepositoryBase


class RedisMixin:
    def __init__(self, redis: Redis, expire_callable: Callable):
        self.redis = redis
        self.expire_callable = expire_callable

    def get(self, key: Any) -> Any:
        return self.redis.get(key)

    def set(self, key: Any, value: Any) -> None:
        self.redis.set(key, value, ex=self.expire_callable())

    def delete(self, key: Any) -> None:
        self.redis.delete(key)

    def delete_by_filter(self, key_filter: Any) -> None:
        for field_key in self.redis.scan_iter(key_filter):
            self.redis.delete(field_key)
