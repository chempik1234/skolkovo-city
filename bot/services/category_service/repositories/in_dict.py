from models.category import CategoryModel
from .base import CategoryRepositoryBase


def _str_dict_to_category_structure(data: dict) -> dict:
    """
    Pass a dict structured like this:

    1. Key is title
    2. Value is `string` (description) or `dict` (nested dict) or `tuple` (desc, link, dict) length up to 3

    Get a dict with objects and ids as keys (for indexing)

    :param data: {"A": {"B": ("good", "https://ya.ru")}}
    :return: {0: Category(title=A, id=0), 1: Category(title=B, id=1, parent_id=0, description="good", link="https://ya.ru")}
    """
    last_id = 0

    def _handle(data: dict, parent_id: int | None = None) -> dict:
        """
        return {_id: model(id=_id), ...}
        """
        nonlocal last_id
        result = {}
        for key, value in data.items():
            category = CategoryModel(
                title=key,
                id=last_id,
                parent_id=parent_id,
                description=None,
                link=None,
            )
            result[last_id] = category
            last_id += 1

            if isinstance(value, dict):
                # recursion
                result.update(_handle(value, category.id))

            elif isinstance(value, str):
                category.description = value

            elif isinstance(value, tuple):  # description | children
                length = len(value)
                if length >= 1:
                    category.description = value[0]
                if length >= 2:
                    category.link = value[1]
                if length >= 3:
                    result.update(_handle(value[2], category.id))
        return result

    return _handle(data)


class CategoryRepositoryInDict(CategoryRepositoryBase):
    def __init__(self, data: dict):
        self.data = _str_dict_to_category_structure(data)
