import json
from typing import Iterable, AsyncGenerator, Any

from aiogram.types import Message

from services.news_service.repositories.base import NewsSenderRepositoryBase
from services.news_service.types import NewsContentMessage


class NewsSenderService:
    def __init__(self, news_repo: NewsSenderRepositoryBase):
        self.news_repo = news_repo

    async def send(self, news_content: Message | Iterable[Message], send_to_ids: Iterable[int]):
        if isinstance(news_content, Message):
            json_content = self.serialize_message(news_content)
        else:
            json_content = json.dumps(news_content)
        await self.news_repo.send(json_content, send_to_ids)

    async def read(self) -> AsyncGenerator[NewsContentMessage, None]:
        async for obj in self.news_repo.read():
            yield obj

    def serialize_message(self, message: Message) -> str:
        return json.dumps(self.serialize_message_json(message))

    def serialize_message_json(self, message) -> dict[str, Any]:
        return {  # send only needed data
            "text": message.text,
            "caption": message.caption,
            "photo": message.photo[-1].file_id if message.photo else None,
            "video": message.video.file_id if message.video else None,
            "animation": message.animation.file_id if message.animation else None,
        }
