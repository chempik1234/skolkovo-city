from bot.services.category_service.repositories.base import CategoryRepositoryBase
from bot.services.user_service.repositories.base import UserRepositoryBase


class CategoryService(UserRepositoryBase):
    def __init__(self, category_repo: CategoryRepositoryBase):
        self.category_repo = category_repo
