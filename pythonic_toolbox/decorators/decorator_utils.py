import asyncio
import functools


def decorate_sync_async(decorating_context, func):
    if asyncio.iscoroutinefunction(func):
        async def wrapper(*args, **kwargs):
            with decorating_context(func, *args, **kwargs) as (args, kwargs):
                return await func(*args, **kwargs)
    else:
        def wrapper(*args, **kwargs):
            with decorating_context(func, *args, **kwargs) as (args, kwargs):
                return func(*args, **kwargs)

    return functools.wraps(func)(wrapper)


def decorate_auto_use_params(func):
    """
    Usage:

    @decorator_auto_params
    def my_decorator(func, key1=val1, key2=val2, ...) -> Callable[..., T]:
        ...

    the decorator with default params can used like this:

    @my_decorator
    def foo():
    ...

    @my_decorator(*args, **kwargs)
    def bar():
    ...

    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # for case @my_decorator
            return func(args[0])
        else:
            # for case @my_decorator(*args, **kwargs)
            return lambda real_func: func(real_func, *args, **kwargs)

    return wrapper
