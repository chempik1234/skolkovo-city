from typing import Callable, Any


class ReloaderRepositoryBase:
    async def run(self):
        raise NotImplementedError()

    def reload(self):
        # you must set it!
        raise NotImplementedError()

    async def stop(self):
        raise NotImplementedError()

    async def notify(self):
        raise NotImplementedError()

    def set_reload_callable(self, callable: Callable[[], Any]):
        self.reload = callable
