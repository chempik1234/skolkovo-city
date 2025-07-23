import structlog
from yandex_cloud_ml_sdk._models.completions.result import Alternative

from .base import AiChatRepositoryBase

logger = structlog.get_logger("yandex_chat_bot")


class AiChatRepositoryYandexCloud(AiChatRepositoryBase):
    def __init__(self, model):
        self.model = model

    async def get_response(self, telegram_id: int | str, question: str) -> str:
        response: list[Alternative] = self.model.run(
            [
                {"role": "system",
                 "text": "Пользователь задал вопрос, которого нет в базе. Попробуй ответить на него сам, и если не "
                         "сможешь, то переведи на колл-цнентр +74959560033. Пиши кратко и по делу: ответ ограничен "
                         "1000 символами"},
                {
                    "role": "user",
                    "text": question,
                },
            ]
        )

        return '\n\n'.join([i.text for i in response])
