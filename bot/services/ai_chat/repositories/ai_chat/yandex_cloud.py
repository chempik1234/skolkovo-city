import asyncio
from datetime import datetime
from typing import Callable, Any, Awaitable, Dict, Coroutine

import structlog
from yandex_cloud_ml_sdk import AsyncYCloudML
from yandex_cloud_ml_sdk._assistants.assistant import AsyncAssistant
from yandex_cloud_ml_sdk._models.completions.model import GPTModel
from yandex_cloud_ml_sdk._models.completions.result import Alternative
from yandex_cloud_ml_sdk._threads.thread import AsyncThread
from yandex_cloud_ml_sdk._types.expiration import ExpirationPolicy

from init.init_0 import bot_config
from .base import AiChatRepositoryBase
from .thread_storage.base import ThreadStorageRepositoryBase

logger = structlog.get_logger("yandex_chat_bot")


class AiChatRepositoryYandexCloud(AiChatRepositoryBase):
    def __init__(self, sdk: AsyncYCloudML, model: GPTModel,
                 function_map: Dict[str, Callable[[Any, Any], Awaitable[Any]]],
                 threads_storage_repo: ThreadStorageRepositoryBase,
                 tools):
        """
        Create Yandex cloud async assistant from model
        :param function_map: ``dict`` object for tools, don't use keys starting with ``'_'``, that's for class methods
        """
        self.sdk = sdk
        self.model = model
        self.function_map = function_map.copy()
        self.assistant: AsyncAssistant | None = None
        self.threads_storage_repo = threads_storage_repo

        self.tools = []

        self.create_tools(tools)

    def create_tools(self, tools):
        self.tools = tools + [
            self.sdk.tools.function(
                name="_get_chat_story",
                description="If user asks you about context (chat story) or makes a following question, read it here",
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": [],
                }
            ),
        ]
        self.function_map["_get_chat_story"] = self._get_chat_story

    async def create_assistant(self):
        self.assistant = await self.sdk.assistants.create(self.model, tools=self.tools)

    async def get_thread_for_user(self, telegram_id: int | str) -> AsyncThread:
        existing_thread_key: str | None = await self.threads_storage_repo.get_thread_key_for_user(telegram_id)
        if existing_thread_key is None:
            thread = await self.create_thread(telegram_id)
        else:
            thread = await self.get_thread(existing_thread_key)

        return thread

    async def get_thread(self, thread_id: str) -> AsyncThread | None:
        try:
            thread = await self.sdk.threads.get(thread_id)
            if thread is None:
                raise Exception(f"No thread with id {thread_id} exists")
            return thread
        except:  # nah I don't know any other way to know
            return None

    async def create_thread(self, telegram_id: int | str) -> AsyncThread:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        thread = await self.sdk.threads.create(
            name=f"user-{telegram_id}-{timestamp}-{bot_config.BOT_INSTANCE_NAME}",
            description=f"Conversation for user {telegram_id} started at {timestamp}",
            labels={
                "container_id": bot_config.BOT_INSTANCE_NAME,
                "user_id": str(telegram_id),
                "session_type": "http_api"
            },
            ttl_days=1,
            expiration_policy=ExpirationPolicy.SINCE_LAST_ACTIVE,
        )

        asyncio.create_task(self.threads_storage_repo.set_thread_key_for_user(telegram_id, thread.id))
        return thread

    async def get_response(self, telegram_id: int | str, question: str) -> str:
        if not self.assistant:
            await self.create_assistant()

        thread = await self.get_thread_for_user(telegram_id)

        is_there_system_message = False
        async for _ in thread:
            is_there_system_message = True
        if not is_there_system_message:
            await thread.write(
                {"role": "user",
                 "text": "Пользователь задал вопрос, которого нет в базе. Попробуй ответить на него сам, и если не "
                         "сможешь, то переведи на колл-центр +74959560033. Пиши кратко и по делу, в формате Markdown под "
                         "мессенджер телеграм"}
            )
        await thread.write({
            "role": "user",
            "text": question,
        })

        run = await self.assistant.run_stream(thread)
        event = None
        async for event in run:
            if event.tool_calls:
                tool_results = await self.tool_processor(event.tool_calls, thread, telegram_id)
                await run.submit_tool_results(tool_results)

        return event.text

    async def tool_processor(self, tool_calls, thread: AsyncThread, telegram_id: int | str):
        result = []
        for tool_call in tool_calls:
            assert tool_call.function

            arguments = tool_call.function.arguments

            function_name = tool_call.function.name

            # use user_id for context
            if function_name.startswith("_"):
                arguments["telegram_id"] = telegram_id
                arguments["thread"] = thread

            function = self.function_map[function_name]

            answer = str(await function(**arguments))  # type: ignore[operator]

            result.append({'name': tool_call.function.name, 'content': answer})
        return result

    async def _get_chat_story(self, thread: AsyncThread, *args, **kwargs) -> str:
        result = [message.text async for message in thread]
        if result:
            return "\n\nnext_data_piece:\n\n".join(result)
        return "empty data, brand new thread"
