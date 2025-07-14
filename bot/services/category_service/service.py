from models.category import CategoryModel
from .repositories.base import CategoryRepositoryBase


class CategoryService:
    def __init__(self, category_repo: CategoryRepositoryBase):
        self.category_repo = category_repo

    async def get_object(self, _id: int | None) -> CategoryModel | None:
        return await self.category_repo.get_object(_id)

    async def get_children_by_id(self, parent_id: int | None) -> list[CategoryModel]:
        return await self.category_repo.get_children_by_id(parent_id)

    async def has_children(self, parent_id: int | None) -> bool:
        return await self.category_repo.has_children(parent_id)

    async def reload_categories(self):
        await self.category_repo.reload_categories()
