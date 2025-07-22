from typing import Iterable, Any

import numpy as np

from ai_utils import embedding_from_bytes
from models.ai_chat import Question


class QuestionLookupRepositoryBase:
    async def get_related_question(self, question: str, questions: Iterable[str]) -> str:
        raise NotImplementedError()

    async def get_similarity(self, db_embedding: np.ndarray, new_question: str) -> Any:
        new_embedding = await self.get_embedding(new_question)

        return (np.dot(new_embedding, db_embedding) /
                (np.linalg.norm(new_embedding) * np.linalg.norm(db_embedding)))

    async def get_embedding(self, question: str) -> np.ndarray:
        raise NotImplementedError()


