import asyncio
import uuid

from db.models import UserDataModel
from models.user import UserModel
from .repositories.base import UserRepositoryBase


class UserService:
    def __init__(self, user_repo: UserRepositoryBase):
        self.user_repo = user_repo

    def _to_model(self, result: UserDataModel) -> UserModel:
        return UserModel(
            telegram_id=result.telegram_id,
            full_name=result.full_name,
            email=result.email,
            is_admin=result.is_admin,
            personal_data_agreement=result.personal_data_agreement
        )

    async def _get_object(self, **kwargs) -> UserDataModel | None:
        # TODO: add cache check
        result: UserDataModel | None = await self.user_repo.get_object(**kwargs)
        # TODO: add cache set
        return result

    async def get_object(self, **kwargs) -> UserModel | None:
        result: UserDataModel | None = await self._get_object(**kwargs)
        if not result:
            return None
        return self._to_model(result)

    async def update_data(self, telegram_id: int, data: dict, create_if_absent: bool = False) -> None:
        existing_object = await self._get_object(telegram_id=telegram_id)

        if not existing_object:
            if not create_if_absent:
                raise ValueError(f"user with telegram id {telegram_id} doesn't exist")

            object_data = data.copy()
            object_data["telegram_id"] = telegram_id
            existing_object = await self.user_repo.create_object(object_data)

        await self.user_repo.update_data(existing_object, data)
        # TODO: add cache invalidation

    async def create_object(self, object_data: dict) -> UserModel:
        telegram_id = object_data.get("telegram_id")
        existing_object = await self.get_object(telegram_id=telegram_id)
        if existing_object:
            raise ValueError(f"user with telegram id {telegram_id} already exists")

        result: UserDataModel = await self.user_repo.create_object(object_data)
        return self._to_model(result)
