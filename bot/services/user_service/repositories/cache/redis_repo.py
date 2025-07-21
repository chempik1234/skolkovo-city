import json
from typing import Any

from redis import Redis
from sqlalchemy.orm import Mapped

from db.models import UserDataModel
from services.user_service.repositories.cache.base import UserCacheRepositoryBase


class UserCacheRepositoryRedis(UserCacheRepositoryBase):
    def __init__(self, redis: Redis, expire_seconds: int = 600):
        self.redis = redis
        self.expire_seconds = expire_seconds

    def _deserialize(self, data: dict) -> UserDataModel:
        model = UserDataModel()
        for k, v in data.items():
            if hasattr(model, k):
                setattr(model, k, v)
        return model

    def _serialize(self, model: UserDataModel) -> str:
        d = {
            "telegram_id": model.telegram_id,
            # "full_name": model.full_name,
            # "email": model.email,
            # "personal_data_agreement": model.personal_data_agreement,
            "is_admin": model.is_admin,
            "language": model.language,
            "is_banned": model.is_banned,
        }
        return json.dumps(d)

    def get_object(self, telegram_id: int | str) -> UserDataModel | None:
        key = str(telegram_id)
        result: None | bytes = self.redis.get(key)
        if result is None:
            return None
        data = json.loads(result)
        return self._deserialize(data)

    def invalidate_object(self, telegram_id: int | str) -> None:
        key = str(telegram_id)
        self.redis.delete(key)
        for field_key in self.redis.scan_iter(f"{key}__*"):
            self.redis.delete(field_key)

    def cache_object(self, user: UserDataModel) -> None:
        self.redis.set(str(user.telegram_id), self._serialize(user), ex=self.expire_seconds)

    def cache_object_field(self, user: UserDataModel, field_name: str = "telegram_id") -> None:
        if not hasattr(user, field_name):
            raise AttributeError("field doesn't exists")
        value = getattr(user, field_name)
        if type(value) is bool:
            value = 1 if value else 0
        self.redis.set(f"{user.telegram_id}__{field_name}", value, ex=self.expire_seconds)

    def get_object_field(self, telegram_id, field_name: str) -> Any:
        result = self.redis.get(f"{telegram_id}__{field_name}")
        if result is None:
            return None
        if UserDataModel.__annotations__.get(field_name, None) is Mapped[bool]:
            result = True if int(result) == 1 else False
        return result

    def get_objects_field(self, field_name: str) -> list[Any] | None:
        result_list: None | bytes = self.redis.get(f"__{field_name}")
        if result_list is None:
            return None
        return json.loads(result_list)

    def cache_objects_field(self, values: list[Any], field_name: str) -> None:
        self.redis.set(f"__{field_name}", json.dumps(values), ex=self.expire_seconds)
