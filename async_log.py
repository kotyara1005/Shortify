import asyncio
import logging
from functools import wraps


def async_log_exception(logger, *, reraise=True):
    if isinstance(logger, str):
        logger = logging.getLogger(logger)

    def decorator(coroutine):
        @wraps(coroutine)
        async def wrapper(*args, **kwargs):
            try:
                return await coroutine(*args, **kwargs)
            except:
                logger.exception(
                    'Exception occurred in {}'.format(coroutine.__name__)
                )
                if reraise:
                    raise
        return wrapper
    return decorator


@async_log_exception(logger=logging.getLogger(__name__), reraise=False)
async def error():
    raise Exception('asdfasdf')


class AsyncOnlyOne:
    _lock = asyncio.Lock()

    def __call__(self, coroutine):
        @wraps(coroutine)
        async def wrapper(*args, **kwargs):
            async with self._lock:
                return await coroutine(*args, **kwargs)

        return wrapper


@AsyncOnlyOne()
async def test():
    print('test')


def main():
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(error())
    loop.run_until_complete(asyncio.gather(test(), test()))


if __name__ == '__main__':
    main()
