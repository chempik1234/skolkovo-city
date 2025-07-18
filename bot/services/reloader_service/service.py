import asyncio
from typing import Callable, Any

from services.category_service.repositories.base import CategoryRepositoryBase
from services.reloader_service.repositories.base import ReloaderRepositoryBase


class ReloaderService:
    # logic is inside base repo
    def __init__(self, reloader_repo: ReloaderRepositoryBase, reload_callable: Callable[[], Any]):
        self.repo = reloader_repo
        self.repo.set_reload_callable(reload_callable)

    async def run_forever(self):
        await self.repo.run()

    async def stop(self):
        await self.repo.stop()

    async def reload_instances(self):
        asyncio.create_task(self.repo.notify())

