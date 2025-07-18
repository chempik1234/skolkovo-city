from typing import Iterable, AsyncGenerator, Any


class NewsSenderRepositoryBase:
    async def send(self, json_content: str, send_to_ids: Iterable[int]):
        raise NotImplementedError()

    def read(self) -> AsyncGenerator[dict[str, int | dict[str, Any]], None]:
        """
        Iterate through messages in format:
        {"telegram_id": 123, "content": <check service serialize method>}
        """
        raise NotImplementedError()
