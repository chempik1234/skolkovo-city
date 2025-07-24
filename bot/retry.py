from typing import Callable, TypeVar, Any, Coroutine, Awaitable, AsyncGenerator, Tuple

import structlog

T = TypeVar('T')

logger = structlog.get_logger("retry_function")


async def retry_async(
        retry_callable: Callable[[Any], Coroutine[Any, Any, T]],
        tries: int = 2,
        on_retry_callable: Callable[[], Awaitable] | None = None,
        *function_args, **function_kwargs
) -> T:
    exception = None
    for _ in range(tries):
        try:
            return await retry_callable(*function_args, **function_kwargs)
        except Exception as e:
            logger.warning("function raised exception, retrying", exc_info=e, function=retry_callable)
            exception = e

            await on_retry_callable()
    raise exception


async def retry_async_generator(
        retry_callable: Callable[[Any], Coroutine[Any, Any, T]],
        tries: int = 2,
        function_args: tuple = (),
        function_kwargs: dict[str, Any] = {},
) -> AsyncGenerator[Tuple[bool, T | None], None]:
    """
    yield (is_success, result after each try)
    """
    exception = None
    for _ in range(tries):
        try:
            yield True, await retry_callable(*function_args, **function_kwargs)
        except Exception as e:
            logger.warning("function raised exception, will retry after yield", exc_info=e, function=retry_callable)
            exception = e

            yield False, exception
    raise exception