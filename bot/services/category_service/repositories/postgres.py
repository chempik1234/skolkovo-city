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
            query_result = await db_session.execute(select(CategoryDataModel).
                                                    order_by(CategoryDataModel.order_num, CategoryDataModel.id))
            objects_list: Iterable[CategoryDataModel] = query_result.scalars().all()

        result = {}

        for category in objects_list:
            result[category.id] = CategoryModel(id=category.id, parent_id=category.parent_id,
                                                title_ru=category.title_ru, title_en=category.title_en,
                                                description_ru=category.description_ru,
                                                description_en=category.description_en, link=category.link,
                                                images_urls=category.images_urls, order_num=category.order_num,)
        self.data = defaultdict(lambda: None, result)
