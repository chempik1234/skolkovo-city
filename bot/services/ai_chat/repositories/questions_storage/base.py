from typing import Iterable

import numpy as np
from numpy.f2py.symbolic import Language

from db.models import QuestionDataModel


class QuestionsStorageRepositoryBase:
    async def get_answered_questions(self, language: Language) -> Iterable[QuestionDataModel]:
        raise NotImplementedError()

    async def set_embedding(self, existing_object: QuestionDataModel, embedding: np.ndarray):
        raise NotImplementedError()

    async def create_new_question(self, question: str) -> None:
        raise NotImplementedError()
