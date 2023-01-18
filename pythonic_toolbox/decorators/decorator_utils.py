import asyncio
import functools
import threading


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

    the decorator with default params can be used like this:

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


def method_synchronized(method):
    @functools.wraps(method)
    def inner(self, *args, **kwargs):
        __dict__ = object.__getattribute__(self, '__dict__')
        lock_name_str = f"_{object.__getattribute__(self, '__class__').__name__}__synchronized_lock"
        lock = __dict__.get(lock_name_str, None)
        if lock is None:
            meta_lock_name_str = f"_{object.__getattribute__(self, '__class__').__name__}__synchronized_meta_lock"
            meta_lock = __dict__.setdefault(meta_lock_name_str, threading.Lock())

            with meta_lock:
                lock = __dict__.get(lock_name_str, None)
                if lock is None:
                    lock = threading.RLock()
                    object.__setattr__(self, lock_name_str, lock)
        with lock:
            return method(self, *args, **kwargs)

    return inner
