from typing import Any

from db.models import UserDataModel


class UserStorageRepositoryBase:
    async def get_object(self, **kwargs) -> UserDataModel | None:
        raise NotImplementedError()

    async def update_data(self, existing_object, data_dict) -> None:
        raise NotImplementedError()

    async def create_object(self, data_dict) -> UserDataModel:
        raise NotImplementedError()

    async def get_objects_field(self, field_name: str) -> list[Any] | None:
        raise NotImplementedError()
