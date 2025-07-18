from typing import Any

from sqlalchemy.util import await_only

from db.models import UserDataModel
from models.user import UserModel
from .repositories.cache.base import UserCacheRepositoryBase
from .repositories.storage.base import UserStorageRepositoryBase


class UserService:
    def __init__(self, user_storage_repo: UserStorageRepositoryBase, user_cache_repo: UserCacheRepositoryBase):
        self.user_storage_repo = user_storage_repo
        self.user_cache_repo = user_cache_repo

    def _to_model(self, result: UserDataModel) -> UserModel:
        return UserModel(
            telegram_id=result.telegram_id,
            # full_name=result.full_name,
            # email=result.email,
            is_admin=result.is_admin,
            # personal_data_agreement=result.personal_data_agreement,
            language=result.language,
            is_banned=result.is_banned,
        )

    async def _get_object(self, no_cache_check: bool = False, **kwargs) -> UserDataModel | None:
        result = None
        if not no_cache_check:
            # 1. check cache
            if len(kwargs) == 1 and "telegram_id" in kwargs:  # we can only use cache if there's only telegram id filter
                result: UserDataModel | None = self.user_cache_repo.get_object(kwargs["telegram_id"])

        # 2. if cache can't be checked or there's no object there, we check the storage
        if result is None:
            result: UserDataModel | None = await self.user_storage_repo.get_object(**kwargs)

            # 3. save in cache
            if result is not None:
               self.user_cache_repo.cache_object(result)

        return result

    async def get_object(self, no_cache_check: bool = False, **kwargs) -> UserModel | None:
        result: UserDataModel | None = await self._get_object(no_cache_check=no_cache_check, **kwargs)
        if not result:
            return None
        return self._to_model(result)

    async def update_data(self, telegram_id: int, data: dict, create_if_absent: bool = False) -> None:
        existing_object = await self._get_object(telegram_id=telegram_id, no_cache_check=True)

        if not existing_object:
            if not create_if_absent:
                raise ValueError(f"user with telegram id {telegram_id} doesn't exist")

            object_data = data.copy()
            object_data["telegram_id"] = telegram_id
            existing_object = await self.user_storage_repo.create_object(object_data)

        await self.user_storage_repo.update_data(existing_object, data)
        self.user_cache_repo.invalidate_object(telegram_id)  # invalidate cache after all

    async def create_object(self, object_data: dict, skip_if_exists: bool = False) -> UserModel:
        telegram_id = object_data.get("telegram_id")
        existing_object = await self.get_object(telegram_id=telegram_id, no_cache_check=False)
        if existing_object:
            if skip_if_exists:
                return existing_object
            raise ValueError(f"user with telegram id {telegram_id} already exists")

        result: UserDataModel = await self.user_storage_repo.create_object(object_data)
        return self._to_model(result)

    async def is_banned(self, telegram_id: int, no_cache_check=False) -> bool | None:
        return await self._get_object_field(telegram_id=telegram_id, no_cache_check=no_cache_check, field_name="is_banned")

    async def is_admin(self, telegram_id: int, no_cache_check=False) -> bool | None:
        return await self._get_object_field(telegram_id=telegram_id, no_cache_check=no_cache_check, field_name="is_admin")

    async def _get_object_field(self, telegram_id: int, field_name: str, no_cache_check: bool = False) -> Any:
        result = None
        if not no_cache_check:
            result = self.user_cache_repo.get_object_field(telegram_id, field_name)

        if result is None:
            user = await self._get_object(telegram_id=telegram_id, no_cache_check=no_cache_check)
            if user is None:
                return None

            self.user_cache_repo.cache_object_field(user, field_name=field_name)

            result = getattr(user, field_name)
        return result

    async def get_objects_field(self, field_name: str, no_cache_check: bool = False):
        result = None
        if not no_cache_check:
            result = self.user_cache_repo.get_objects_field(field_name)

        if result is None:
            result = await self.user_storage_repo.get_objects_field(field_name)
            if result is None:
                return None

            self.user_cache_repo.cache_objects_field(result, field_name=field_name)
        return result
