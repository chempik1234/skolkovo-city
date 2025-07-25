from typing import Iterable

from db.models import QuestionDataModel


class AiChatRepositoryBase:
    async def get_response(self, telegram_id: int | str, question: str) -> str:
        raise NotImplementedError()

    async def upload_questions_for_search(self, questions: Iterable[QuestionDataModel]):
        raise NotImplementedError()
