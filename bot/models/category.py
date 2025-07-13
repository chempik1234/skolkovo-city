from pydantic import BaseModel


class CategoryModel(BaseModel):
    title: str
    id: int
    parent_id: int | None
    description: str | None
    link: str | None
