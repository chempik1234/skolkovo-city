from pydantic import BaseModel


class Question(BaseModel):
    id: int
    question: str
    answer_ru: str | None
    answer_en: str | None
    embedding: bytes | None
    category_id: int | None
