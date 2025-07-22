from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.testing import db_spec

from db.models import UserDataModel
from services.postgres_mixin import PostgresMixin
from services.user_service.repositories.storage.base import UserStorageRepositoryBase


class UserStorageRepositoryPostgres(PostgresMixin, UserStorageRepositoryBase):
    def __init__(self, sqlalchemy_session_maker):
        super().__init__(sqlalchemy_session_maker, UserDataModel)

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
