class ThreadStorageRepositoryBase:
    async def get_thread_key_for_user(self, telegram_id: int | str) -> str | None:
        raise NotImplementedError()

    async def set_thread_key_for_user(self, telegram_id: int | str, thread_key: int | str) -> None:
        raise NotImplementedError()
