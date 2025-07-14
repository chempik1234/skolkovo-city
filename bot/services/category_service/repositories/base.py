from models.category import CategoryModel


class CategoryRepositoryBase:
    async def get_object(self, _id: int | None) -> CategoryModel | None:
        raise NotImplementedError()

    async def get_children_by_id(self, parent_id: int | None) -> list[CategoryModel]:
        raise NotImplementedError()

    async def reload_categories(self):
        raise NotImplementedError()

    async def has_children(self, parent_id: int | None) -> bool:
        raise NotImplementedError()
