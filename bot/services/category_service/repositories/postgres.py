import asyncio
from collections import defaultdict
from typing import Iterable

from sqlalchemy import select

from db.models import CategoryDataModel
from models.category import CategoryModel
from .base import CategoryRepositoryBase


class CategoryRepositoryPostgres(CategoryRepositoryBase):
    def __init__(self, session_maker):
        # 1: CategoryModel(id=1), -9999: None
        self.session_maker = session_maker  # one time use

    async def reload_categories(self, *args, **kwargs):
        async with self.session_maker(expire_on_commit=False) as db_session:
            query_result = await db_session.execute(select(CategoryDataModel))
            objects_list = query_result.scalars().all()

        result = {}

        for category in objects_list:
            result[category.id] = CategoryModel(id=category.id, parent_id=category.parent_id,
                                                title=category.title, description=category.description,
                                                link=category.link)
        self.data = defaultdict(lambda: None, result)
