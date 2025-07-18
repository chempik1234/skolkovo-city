from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.testing import db_spec

from db.models import UserDataModel
from services.user_service.repositories.storage.base import UserStorageRepositoryBase


class UserStorageRepositoryPostgres(UserStorageRepositoryBase):
    def __init__(self, sqlalchemy_session_maker):
        self.session_maker = sqlalchemy_session_maker

    def _model_attrs_from_dict(self, data_object, data_dict) -> None:
        for key, value in data_dict.items():
            if value is not None and hasattr(data_object, key):
                setattr(data_object, key, value)

    # def _field_values(self, kwargs) -> dict:
    #     """we better don't specify these as args but use a comprehension: both are possibly unsafe anyway"""
    #
    #     # fields = ["telegram_id", "full_name", "is_admin", "email", "personal_data_agreement"]
    #     return {
    #         field: value for field, value in kwargs.items()
    #         if (
    #                    field == "telegram_id" or field == "full_name" or
    #                    field == "is_admin" or field == "email" or field == "personal_data_agreement"
    #            )
    #            and value is not None
    #     }

    async def get_object(self, **kwargs) -> UserDataModel | None:
        async with self.session_maker(expire_on_commit=False) as db_session:
            filters = kwargs  # self._field_values(kwargs)

            query_result = await db_session.execute(select(UserDataModel).filter_by(**filters))
            return query_result.scalar_one_or_none()

    async def update_data(self, existing_object, data_dict) -> None:
        async with self.session_maker(expire_on_commit=False) as db_session:
            try:
                # data_dict = self._field_values(data_dict)
                self._model_attrs_from_dict(existing_object, data_dict)
                db_session.add(existing_object)
                await db_session.commit()
                await db_session.refresh(existing_object)
                return existing_object
            except IntegrityError:
                await db_session.rollback()

    async def create_object(self, data_dict) -> UserDataModel:
        async with self.session_maker(expire_on_commit=False) as db_session:
            try:
                new_object = UserDataModel()
                self._model_attrs_from_dict(new_object, data_dict)
                db_session.add(new_object)
                await db_session.commit()
                return new_object
            except IntegrityError:
                await db_session.rollback()

    async def get_objects_field(self, field_name: str) -> list[Any] | None:
        async with self.session_maker(expire_on_commit=False) as db_session:
            result = await db_session.execute(select(getattr(UserDataModel, field_name)))
            return result.scalars().all()
