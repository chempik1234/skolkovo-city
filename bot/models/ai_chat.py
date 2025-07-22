from pydantic import BaseModel


class Question(BaseModel):
    id: int
    question: str
    answer: str | None
    embedding: bytes | None
