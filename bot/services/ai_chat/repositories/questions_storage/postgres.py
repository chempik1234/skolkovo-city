from typing import Iterable

import numpy as np

from ai_utils import embedding_to_bytes
from db.models import QuestionDataModel
from services.ai_chat.repositories.questions_storage.base import QuestionsStorageRepositoryBase
from services.postgres_mixin import PostgresMixin
from custom_types import Language, LanguageEnum

from sqlalchemy import or_, and_


class QuestionsStorageRepositoryPostgres(PostgresMixin, QuestionsStorageRepositoryBase):
    model = QuestionDataModel

    def __init__(self, sqlalchemy_session_maker):
        super().__init__(sqlalchemy_session_maker, model=QuestionDataModel)

    async def get_answered_questions(self, language: Language = LanguageEnum.ru,
                                     search_among_category: bool = False,
                                     search_among_non_category: bool = False,
                                     all_languages: bool = False) -> Iterable[QuestionDataModel]:
        # Only category binded
        if search_among_category and not search_among_non_category:
            return await self.get_objects(QuestionDataModel.category_id != None)

        # Only user-typed
        elif search_among_non_category and not search_among_category:
            if all_languages:
                condition = and_(
                    or_(QuestionDataModel.answer_en != None, QuestionDataModel.answer_ru != None),
                    QuestionDataModel.category_id == None,
                )
            else:
                if language == LanguageEnum.en:
                    condition = and_(QuestionDataModel.answer_en != None, QuestionDataModel.category_id == None)
                else:
                    condition = and_(QuestionDataModel.answer_ru != None, QuestionDataModel.category_id == None)

        # Both groups
        else:
            if all_languages:
                condition = or_(
                    QuestionDataModel.answer_en != None,
                    QuestionDataModel.answer_ru != None,
                    QuestionDataModel.category_id != None,
                )
            else:
                if language == LanguageEnum.en:
                    condition = or_(QuestionDataModel.answer_en != None, QuestionDataModel.category_id != None)
                else:
                    condition = or_(QuestionDataModel.answer_ru != None, QuestionDataModel.category_id != None)

        return await self.get_objects(condition)

    async def set_embedding(self, existing_object: model, embedding: np.ndarray):
        existing_object.embedding = embedding_to_bytes(embedding)
        return await self.update_data(existing_object, {"embedding": existing_object.embedding})

    async def create_new_question(self, question: str) -> None:
        if not await self.get_object(question=question):
            await self.create_object(QuestionDataModel(question=question))
