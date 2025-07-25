import asyncio
from typing import Tuple, Any

import numpy as np
import structlog

from ai_utils import embedding_from_bytes
from models.ai_chat import Question
from services.ai_chat.repositories.ai_chat.base import AiChatRepositoryBase
from services.ai_chat.repositories.question_lookup.base import QuestionLookupRepositoryBase
from services.ai_chat.repositories.questions_storage.base import QuestionsStorageRepositoryBase
from services.rate_limiter.repositories.base import RateLimiterException
from services.rate_limiter.service import RateLimiterService
from custom_types import Language, LanguageEnum

logger = structlog.get_logger("services.ai_chat")


class AiChatService:
    def __init__(self,
                 ai_chat_repo: AiChatRepositoryBase,
                 question_lookup_repo: QuestionLookupRepositoryBase,
                 questions_storage_repo: QuestionsStorageRepositoryBase,
                 save_question_rate_limiter: RateLimiterService,
                 ask_ai_rate_limiter: RateLimiterService,
                 ):
        self.ai_chat_repo = ai_chat_repo
        self.question_lookup_repo = question_lookup_repo
        self.questions_storage_repo = questions_storage_repo
        self.save_question_rate_limiter = save_question_rate_limiter
        self.ask_ai_rate_limiter = ask_ai_rate_limiter

    async def get_response(self, telegram_id: int | str, question: str) -> str:
        if await self.ask_ai_rate_limiter.can_user_do_action(telegram_id):
            asyncio.create_task(self.ask_ai_rate_limiter.increase_counter(telegram_id))
            return await self.ai_chat_repo.get_response(telegram_id, question)
        else:
            logger.warning("create new question rate limiter", extra_data={"telegram_id": telegram_id})
            raise RateLimiterException()

    async def get_related_question_from_db(
            self,
            user_question: str,
            language: Language,
            search_among_category: bool = False,
            search_among_non_category: bool = False,
    ) -> Tuple[Question | None, np.float64 | None]:
        """
        accepts a question and returns related question and answer from storage, recalculates embeddings when NULL

        (question, answer_text, category_id, embedding_value)

        if no questions then return ("" "" None)
        """
        user_embedding = await self.question_lookup_repo.get_embedding(user_question.lower())

        async def process_question(question) -> Tuple[np.float64, Question] | None:
            # get embedding from remote API
            if not question.embedding:
                logger.info("new embedding for question", extra_data={"question_id": question.id})

                try:
                    embedding = await self.question_lookup_repo.get_embedding(question.question.lower())
                    await self.questions_storage_repo.set_embedding(question, embedding)
                except Exception as e:
                    logger.error("error while getting embedding for question",
                                 extra_data={"question": question}, exc_info=e)
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

        questions = await self.questions_storage_repo.get_answered_questions(language=language,
                                                                             search_among_category=search_among_category,
                                                                             search_among_non_category=search_among_non_category)

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
        if await self.save_question_rate_limiter.can_user_do_action(telegram_id):
            await self.questions_storage_repo.create_new_question(question)
            await self.save_question_rate_limiter.increase_counter(telegram_id)
        else:
            logger.warning("create new question rate limiter", extra_data={"telegram_id": telegram_id})

    async def upload_questions_for_search(self):
        await self.ai_chat_repo.upload_questions_for_search(
            await self.questions_storage_repo.get_answered_questions(
                search_among_non_category=True, search_among_category=True, all_languages=True,
            )
        )

    async def delete_all_search_indexes(self):
        await self.ai_chat_repo.delete_all_search_indexes()