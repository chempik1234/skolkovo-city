from aio_pika.abc import AbstractQueue, AbstractExchange, AbstractChannel, AbstractConnection, \
    ExchangeType, AbstractIncomingMessage

from services.rabbitmq_mixin import RabbitMQMixin
from services.reloader_service.repositories.base import ReloaderRepositoryBase


class ReloaderRepositoryRabbitMQ(ReloaderRepositoryBase, RabbitMQMixin):
    def __init__(self, url: str, exchange_name: str):
        super().__init__(url, exchange_name, exchange_type=ExchangeType.fanout, routing_key="reloading_queue")

    async def handle_message(self, message: AbstractIncomingMessage):
        self.reload()

    async def notify(self):
        await self.publish(b"woa")
