import json
from typing import Any

from redis import Redis
from sqlalchemy.orm import Mapped

from db.models import UserDataModel
from services.redis_mixin import RedisMixin
from services.user_service.repositories.cache.base import UserCacheRepositoryBase


class UserCacheRepositoryRedis(UserCacheRepositoryBase, RedisMixin):
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
        result: None | bytes = self.get(key)
        if result is None:
            return None
        data = json.loads(result)
        return self._deserialize(data)

    def invalidate_object(self, telegram_id: int | str) -> None:
        key = str(telegram_id)
        self.delete(key)
        self.delete_by_filter(f"{key}__*")

    def cache_object(self, user: UserDataModel) -> None:
        self.set(str(user.telegram_id), self._serialize(user))

    def cache_object_field(self, user: UserDataModel, field_name: str = "telegram_id") -> None:
        if not hasattr(user, field_name):
            raise AttributeError("field doesn't exists")
        value = getattr(user, field_name)
        if type(value) is bool:
            value = 1 if value else 0
        self.set(f"{user.telegram_id}__{field_name}", value)

    def get_object_field(self, telegram_id, field_name: str) -> Any:
        result: bytes | None = self.get(f"{telegram_id}__{field_name}")
        if result is None:
            return None

        field_type = UserDataModel.__annotations__.get(field_name, None)
        if field_type is Mapped[bool]:
            result = True if int(result) == 1 else False
        elif field_type is Mapped[str]:
            result = result.decode("utf8")
        return result

    def get_objects_field(self, field_name: str) -> list[Any] | None:
        result_list: None | bytes = self.get(f"__{field_name}")
        if result_list is None:
            return None
        return json.loads(result_list)

    def cache_objects_field(self, values: list[Any], field_name: str) -> None:
        self.set(f"__{field_name}", json.dumps(values))
