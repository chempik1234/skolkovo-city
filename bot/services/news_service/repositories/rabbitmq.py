import asyncio
import json
from typing import Iterator, Iterable, Any, AsyncGenerator

from aio_pika import ExchangeType
from aio_pika.abc import AbstractIncomingMessage

from services.news_service.repositories.base import NewsSenderRepositoryBase
from services.rabbitmq_mixin import RabbitMQMixin


class NewsSenderRepositoryRabbitMQ(NewsSenderRepositoryBase, RabbitMQMixin):
    def __init__(self, url: str, exchange_name: str):
        super().__init__(url, exchange_name, exchange_type=ExchangeType.DIRECT, queue_name="news", routing_key="news")

    async def send(self, json_content: str, send_to_ids: Iterable[int]):
        for telegram_id in send_to_ids:
            body = ''.join(['{"telegram_id": ', str(telegram_id), ', "content": ', json_content, '}'])
            asyncio.create_task(self.publish(
                body=body.encode('utf-8'),
            ))

    def get_message_data(self, message: AbstractIncomingMessage) -> dict[str, int | dict[str, Any]]:
        queue_message = json.loads(message.body.decode('utf-8'))
        return queue_message

    async def read(self) -> AsyncGenerator[dict[str, int | dict[str, Any]], None]:
        await self.connect()
        async with self.queue.iterator() as queue_iterator:
            async for message in queue_iterator:
                async with message.process():
                    yield self.get_message_data(message)