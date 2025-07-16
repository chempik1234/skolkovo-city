import json

from redis import Redis

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
            "full_name": model.full_name,
            "email": model.email,
            "personal_data_agreement": model.personal_data_agreement,
            "is_admin": model.is_admin,
            "language": model.language
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
        self.redis.delete(str(telegram_id))

    def cache_object(self, user: UserDataModel) -> None:
        self.redis.set(str(user.telegram_id), self._serialize(user), ex=self.expire_seconds)
