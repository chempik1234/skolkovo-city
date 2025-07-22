from typing import Iterable

import numpy as np

from ai_utils import embedding_to_bytes
from db.models import QuestionDataModel
from services.ai_chat.repositories.questions_storage.base import QuestionsStorageRepositoryBase
from services.postgres_mixin import PostgresMixin


class QuestionsStorageRepositoryPostgres(PostgresMixin, QuestionsStorageRepositoryBase):
    model = QuestionDataModel

    def __init__(self, sqlalchemy_session_maker):
        super().__init__(sqlalchemy_session_maker, model=QuestionDataModel)

    async def get_answered_questions(self) -> Iterable[QuestionDataModel]:
        return await self.get_objects()

    async def set_embedding(self, existing_object: model, embedding: np.ndarray):
        existing_object.embedding = embedding_to_bytes(embedding)
        return await self.update_data(existing_object, {"embedding": existing_object.embedding})
