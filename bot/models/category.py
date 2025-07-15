from pydantic import BaseModel


class CategoryModel(BaseModel):
    title: str
    id: int
    parent_id: int | None
    link: str | None

    description_ru: str | None
    description_en: str | None
