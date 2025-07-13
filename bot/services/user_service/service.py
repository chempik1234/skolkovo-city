from .repositories.base import UserRepositoryBase


class UserService:
    def __init__(self, user_repo: UserRepositoryBase):
        self.user_repo = user_repo
