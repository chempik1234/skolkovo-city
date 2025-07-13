from .repositories.base import CategoryRepositoryBase


class CategoryService:
    def __init__(self, category_repo: CategoryRepositoryBase):
        self.category_repo = category_repo
