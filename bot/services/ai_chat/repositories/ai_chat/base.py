class AiChatRepositoryBase:
    async def get_response(self, telegram_id: int | str, question: str) -> str:
        raise NotImplementedError()
