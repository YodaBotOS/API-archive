import asyncio
import functools
from asyncio import get_event_loop as asyncEvent

def executor(loop: asyncio.AbstractEventLoop = None): 
    """A decorator that wraps a sync function in an executor, changing it into an async function."""

    loop = loop or asyncEvent()

    def decorator(func):
        @functools.wraps(func)
        async def sync_wrapper(*args, **kwargs):
            """
            Asynchronous function that wraps a sync function with an executor.
            """

            internal_function = functools.partial(func, *args, **kwargs)
            return await loop.run_in_executor(None, internal_function)

        return sync_wrapper

    return decorator