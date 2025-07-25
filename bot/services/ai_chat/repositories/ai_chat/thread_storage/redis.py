from init.init_0 import bot_config
from services.ai_chat.repositories.ai_chat.thread_storage.base import ThreadStorageRepositoryBase
from services.redis_mixin import RedisMixin


class ThreadStorageRepositoryRedis(RedisMixin, ThreadStorageRepositoryBase):
    def _key(self, telegram_id: int | str):
        return f"thread__{telegram_id}"   # __{bot_config.BOT_INSTANCE_NAME}"

    async def get_thread_key_for_user(self, telegram_id: int | str, update_expiracy: bool = False) -> str | None:
        result = self.get(self._key(telegram_id))
        if result is None:
            return None
        if update_expiracy:
            await self.set_thread_key_for_user(telegram_id, result)
        return result.decode("utf-8")

    async def set_thread_key_for_user(self, telegram_id: int | str, thread_key: str) -> None:
        self.set(self._key(telegram_id), thread_key)
