from models.category import CategoryModel


class CategoryRepositoryBase:
    data: dict[int, CategoryModel | None] = {}

    async def get_object(self, _id: int | None) -> CategoryModel | None:
        return self.data[_id]

    async def get_children_by_id(self, parent_id: int | None) -> list[CategoryModel]:
        return [v for v in self.data.values() if isinstance(v, CategoryModel) and v.parent_id == parent_id]

    def reload_categories(self, *args, **kwargs):
        pass
