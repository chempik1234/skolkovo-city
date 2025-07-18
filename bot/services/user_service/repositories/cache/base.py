from typing import Any

from db.models import UserDataModel


class UserCacheRepositoryBase:
    def get_object(self, telegram_id: int | str) -> UserDataModel | None:
        raise NotImplementedError()

    def invalidate_object(self, telegram_id: int | str) -> None:
        raise NotImplementedError()

    def cache_object(self, user: UserDataModel) -> None:
        raise NotImplementedError()

    def cache_object_field(self, user: UserDataModel, field_name: str = "telegram_id") -> None:
        raise NotImplementedError()

    def get_object_field(self, telegram_id, field_name: str) -> Any:
        raise NotImplementedError()

    def get_objects_field(self, field_name: str) -> list[Any] | None:
        raise NotImplementedError()

    def cache_objects_field(self, values: list[Any], field_name: str) -> None:
        raise NotImplementedError()
