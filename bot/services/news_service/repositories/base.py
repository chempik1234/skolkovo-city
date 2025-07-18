from typing import Iterator, Iterable


class NewsSenderRepositoryBase:
    async def send(self, json_content: str, send_to_ids: Iterable[int]):
        raise NotImplementedError()

    def read(self) -> Iterator[dict[str, str]]:
        """
        Iterate through messages in format:
        {
        """
        raise NotImplementedError()
