from typing import Iterable

import numpy as np

from db.models import QuestionDataModel


class QuestionsStorageRepositoryBase:
    async def get_answered_questions(self) -> Iterable[QuestionDataModel]:
        raise NotImplementedError()

    async def set_embedding(self, existing_object: QuestionDataModel, embedding: np.ndarray):
        raise NotImplementedError()
