import aio_pika
from aio_pika import Connection, Message
from aio_pika.abc import AbstractQueue, AbstractExchange, AbstractChannel, AbstractConnection
from pika.exchange_type import ExchangeType

from services.reloader_service.repositories.base import ReloaderRepositoryBase


class ReloaderRepositoryRabbitMQ(ReloaderRepositoryBase):
    def __init__(self, url: str, exchange_name: str):
        self.exchange_name = exchange_name
        self.exchange: AbstractExchange | None = None
        self.url = url
        self.channel: AbstractChannel | None = None
        self.connection: AbstractConnection | None = None
        self.queue: AbstractQueue | None = None

    async def connect(self):
        self.connection = await aio_pika.connect(self.url)
        self.channel = await self.connection.channel()

    async def run(self):
        if not self.connection:
            await self.connect()

        if not self.exchange:
            # exchange so we send everyone
            self.exchange = await self.channel.declare_exchange(name=self.exchange_name, type=ExchangeType.fanout)

        if not self.queue:
            self.queue = await self.channel.declare_queue(name="", exclusive=True)
            await self.queue.bind(self.exchange, routing_key="reloading_queue")
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    self.reload()

    async def stop(self):
        if self.connection:
            await self.connection.close()

    async def notify(self):
        if self.exchange:
            await self.exchange.publish(Message(body=b"woa"), routing_key="reloading_queue")
