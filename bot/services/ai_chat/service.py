import asyncio
from typing import Tuple

import structlog

from ai_utils import embedding_from_bytes
from services.ai_chat.repositories.ai_chat.base import AiChatRepositoryBase
from services.ai_chat.repositories.question_lookup.base import QuestionLookupRepositoryBase
from services.ai_chat.repositories.questions_storage.base import QuestionsStorageRepositoryBase

logger = structlog.get_logger("services.ai_chat")


class AiChatService:
    def __init__(self,
                 ai_chat_repo: AiChatRepositoryBase,
                 question_lookup_repo: QuestionLookupRepositoryBase,
                 questions_storage_repo: QuestionsStorageRepositoryBase,
                 ):
        self.ai_chat_repo = ai_chat_repo
        self.question_lookup_repo = question_lookup_repo
        self.questions_storage_repo = questions_storage_repo

    async def get_response(self, telegram_id: int | str, question: str) -> str:
        return await self.ai_chat_repo.get_response(telegram_id, question)

    async def get_related_question_from_db(self, user_question: str) -> Tuple[str, str]:
        """
        accepts a question and returns related question and answer from storage, recalculates embeddings when NULL
        """
        async def process_question(question):
            # cache embedding locally e.g. Postgres
            if not question.embedding:
                logger.info("new embedding for question", extra_data={"question_id": question.id})

                embedding = await self.question_lookup_repo.get_embedding(question.question)
                await self.questions_storage_repo.set_embedding(question, embedding)
            # or get from cache
            else:
                embedding = embedding_from_bytes(question.embedding)

            return (
                await self.question_lookup_repo.get_similarity(embedding, user_question),
                question.question,
                question.answer,
            )

        questions = await self.questions_storage_repo.get_answered_questions()

        similarities = await asyncio.gather(
            *[process_question(question) for question in questions]
        )

        # max_value, related_question = max([i for i in similarities if isinstance(i, tuple)])
        max_value = related_question = answer = None
        for result in similarities:
            if not isinstance(result, tuple):
                continue
            if max_value is None or max_value is not None and max_value < result[0]:
                max_value, related_question = answer = result

        return related_question
