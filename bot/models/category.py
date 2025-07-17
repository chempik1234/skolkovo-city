from pydantic import BaseModel


class CategoryModel(BaseModel):
    title_ru: str
    title_en: str | None
    id: int
    parent_id: int | None
    link: str | None

    order_num: int

    images_urls: list[str] | None

    description_ru: str | None
    description_en: str | None
