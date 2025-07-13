from .base import UserRepositoryBase


class UserRepositoryPostgres(UserRepositoryBase):
    def __init__(self, sqlalchemy_session_maker):
        self.db = sqlalchemy_session_maker