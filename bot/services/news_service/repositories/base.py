from typing import Iterable, AsyncGenerator, Any

from services.news_service.types import NewsContentMessage


class NewsSenderRepositoryBase:
    async def send(self, json_content: str, send_to_ids: Iterable[int]):
        raise NotImplementedError()

    def read(self) -> AsyncGenerator[NewsContentMessage, None]:
        """
        Iterate through messages in format:
        {"telegram_id": 123, "content": <check service serialize method>}
        or
        {"telegram_id": 123, "content": [<check service serialize method>, ...] }
        """
        raise NotImplementedError()
