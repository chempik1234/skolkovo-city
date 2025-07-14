import asyncio

import async_to_sync

from models.category import CategoryModel
from .repositories.base import CategoryRepositoryBase


class CategoryService:
    def __init__(self, category_repo: CategoryRepositoryBase, *args, **kwargs):
        self.category_repo = category_repo
        self.reload_categories(*args, **kwargs)

    async def get_object(self, _id: int | None) -> CategoryModel | None:
        return await self.category_repo.get_object(_id)

    async def get_children_by_id(self, parent_id: int | None) -> list[CategoryModel]:
        return await self.category_repo.get_children_by_id(parent_id)

    def reload_categories(self, *args, **kwargs):
        async_to_sync.function(self.category_repo.reload_categories(*args, **kwargs))
