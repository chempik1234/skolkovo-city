import asyncio
from typing import Tuple, Any

import numpy as np
import structlog

from ai_utils import embedding_from_bytes
from models.ai_chat import Question
from services.ai_chat.repositories.ai_chat.base import AiChatRepositoryBase
from services.ai_chat.repositories.question_lookup.base import QuestionLookupRepositoryBase
from services.ai_chat.repositories.questions_storage.base import QuestionsStorageRepositoryBase
from services.rate_limiter.service import RateLimiterService
from custom_types import Language, LanguageEnum

logger = structlog.get_logger("services.ai_chat")


class AiChatService:
    def __init__(self,
                 ai_chat_repo: AiChatRepositoryBase,
                 question_lookup_repo: QuestionLookupRepositoryBase,
                 questions_storage_repo: QuestionsStorageRepositoryBase,
                 rate_limiter: RateLimiterService,
                 ):
        self.ai_chat_repo = ai_chat_repo
        self.question_lookup_repo = question_lookup_repo
        self.questions_storage_repo = questions_storage_repo
        self.rate_limiter = rate_limiter

    async def get_response(self, telegram_id: int | str, question: str) -> str:
        return await self.ai_chat_repo.get_response(telegram_id, question)

    async def get_related_question_from_db(self, user_question: str, language: Language) -> Tuple[Question | None, np.float64 | None]:
        """
        accepts a question and returns related question and answer from storage, recalculates embeddings when NULL

        (question, answer_text, category_id, embedding_value)

        if no questions then return ("" "" None)
        """
        user_embedding = await self.question_lookup_repo.get_embedding(user_question)

        async def process_question(question) -> Tuple[np.float64, Question] | None:
            # get embedding from remote API
            if not question.embedding:
                logger.info("new embedding for question", extra_data={"question_id": question.id})

                try:
                    embedding = await self.question_lookup_repo.get_embedding(question.question)
                    await self.questions_storage_repo.set_embedding(question, embedding)
                except Exception as e:
                    logger.error("error while getting embedding for question",
                                 extra_data={"question_id": question.id}, exc_info=e)
                    return None
            # or get from cache e.g. Postgres
            else:
                embedding = embedding_from_bytes(question.embedding)

            try:
                return (
                    await self.question_lookup_repo.get_similarity(embedding, user_embedding),
                    question,
                )
            except Exception as e:
                logger.error("error while getting similarity for question",
                             extra_data={"question_id": question.id, 'user_question': user_question}, exc_info=e)
                return None

        questions = await self.questions_storage_repo.get_answered_questions(language=language)

        similarities = await asyncio.gather(
            *[process_question(question) for question in questions]
        )

        # max_value, related_question = max([i for i in similarities if isinstance(i, tuple)])
        max_value = question = None
        for result in similarities:
            if not isinstance(result, tuple):
                continue
            if max_value is None or max_value is not None and max_value < result[0]:
                max_value, question = result

        return question, max_value

    async def create_new_question(self, telegram_id: int | str, question: str) -> None:
        if await self.rate_limiter.can_user_do_action(telegram_id):
            await self.questions_storage_repo.create_new_question(question)
            await self.rate_limiter.increase_counter(telegram_id)
        else:
            logger.warning("create new question rate limiter", extra_data={"telegram_id": telegram_id})
