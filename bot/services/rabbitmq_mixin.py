import logging

import aio_pika
from aio_pika import Message
from aio_pika.abc import AbstractExchange, AbstractChannel, AbstractConnection, AbstractQueue, ExchangeType, \
    AbstractIncomingMessage

logger = logging.getLogger("rabbitmq_mixin")


class RabbitMQMixin:
    def __init__(self, url: str, exchange_name: str, exchange_type: ExchangeType, routing_key: str, queue_name: str = ""):
        self.exchange_name = exchange_name
        self.exchange: AbstractExchange | None = None
        self.exchange_type = exchange_type
        self.routing_key = routing_key
        self.queue_name = queue_name
        self.url = url
        self.channel: AbstractChannel | None = None
        self.connection: AbstractConnection | None = None
        self.queue: AbstractQueue | None = None

    async def connect(self):
        if self.connection:
            return
        self.connection = await aio_pika.connect(self.url)
        self.channel = await self.connection.channel()

        if not self.exchange:
            # exchange so we send everyone
            self.exchange = await self.channel.declare_exchange(name=self.exchange_name, type=self.exchange_type)

        if not self.queue:
            self.queue = await self.channel.declare_queue(name=self.queue_name)
            await self.queue.bind(self.exchange, routing_key=self.routing_key)

        logger.info("connected rabbitmq_mixin", extra={"url": self.url})

    async def run(self):
        await self.connect()
        logger.info("starting consumer", extra={"url": self.url, "queue_name": self.queue_name})
        await self.queue.consume(self.handle_message)

    async def handle_message(self, message: AbstractIncomingMessage):
        raise NotImplementedError()

    async def stop(self):
        if self.connection:
            logger.info("stop rabbitmq", extra={"url": self.url, "queue_name": self.queue_name})
            await self.connection.close()

    async def publish(self, body: bytes, routing_key: str | None = None):
        if not self.exchange:
            await self.connect()
        if routing_key is None:
            routing_key = self.routing_key
        await self.exchange.publish(Message(body=body), routing_key=routing_key)
