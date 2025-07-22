import structlog
from .base import AiChatRepositoryBase

logger = structlog.get_logger("yandex_chat_bot")


class AiChatRepositoryYandexCloud(AiChatRepositoryBase):
    def __init__(self, model):
        self.model = model

    async def get_response(self, telegram_id: int | str, question: str) -> str:
        response = self.model.run(
            [
                {"role": "system",
                 "text": "Пользователь спросил у тебя что-то, ищи ответ в базе знаний и если не найдёшь, "
                         "то порекомендуй обратиться в колл-центр. В случае, если он спрашивает что-то нерелевантное, "
                         "скажи ему об этом"},
                {
                    "role": "user",
                    "text": question,
                },
            ]
        )

        return '\n\n'.join([str(i) for i in response])
