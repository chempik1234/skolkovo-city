from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

from ai_utils import embedding_from_bytes
from models.ai_chat import Question
from services.ai_chat.repositories.question_lookup.base import QuestionLookupRepositoryBase


class QuestionLookupRepositorySentenceTransformer(QuestionLookupRepositoryBase):
    def __init__(self, embedding_model: SentenceTransformer):
        self.embedding_model = embedding_model

    async def get_related_question(self, question: str, questions: Iterable[Question]) -> str:
        pass

    async def get_similarity(self, existing_question: Question, new_question: str):
        new_embedding = await self.get_embedding(new_question)
        db_embedding = embedding_from_bytes(existing_question.embedding)
        return (np.dot(new_embedding, db_embedding) /
                (np.linalg.norm(new_embedding) * np.linalg.norm(db_embedding)))

    async def get_embedding(self, question: str) -> np.ndarray:
        return self.embedding_model.encode(question, convert_to_numpy=True)
