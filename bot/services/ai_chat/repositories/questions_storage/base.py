from typing import Iterable

import numpy as np
from numpy.f2py.symbolic import Language

from custom_types import LanguageEnum
from db.models import QuestionDataModel


class QuestionsStorageRepositoryBase:
    async def get_answered_questions(self, language: Language = LanguageEnum.ru,
                                     search_among_category: bool = False,
                                     search_among_non_category: bool = False,
                                     all_languages: bool = False) -> Iterable[QuestionDataModel]:
        raise NotImplementedError()

    async def set_embedding(self, existing_object: QuestionDataModel, embedding: np.ndarray):
        raise NotImplementedError()

    async def create_new_question(self, question: str) -> None:
        raise NotImplementedError()
