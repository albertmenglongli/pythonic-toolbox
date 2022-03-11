import asyncio
import functools
import inspect
import time
from contextlib import contextmanager
from inspect import Parameter
from typing import Callable, Union, TypeVar, Any

from pythonic_toolbox.decorators.decorator_utils import decorate_auto_use_params, decorate_sync_async

T = TypeVar("T")


def ignore_unexpected_kwargs(func: Callable[..., T]) -> Callable[..., T]:
    def filter_kwargs(kwargs: dict) -> dict:
        sig = inspect.signature(func)
        # Parameter.VAR_KEYWORD - a dict of keyword arguments that aren't bound to any other
        if any(map(lambda p: p.kind == Parameter.VAR_KEYWORD, sig.parameters.values())):
            # if **kwargs exists, return directly
            return kwargs

        _params = list(filter(lambda p: p.kind in {Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD},
                              sig.parameters.values()))

        res_kwargs = {
            param.name: kwargs[param.name]
            for param in _params if param.name in kwargs
        }
        return res_kwargs

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        kwargs = filter_kwargs(kwargs)
        return func(*args, **kwargs)

    return wrapper


@decorate_auto_use_params
def duration(func: Callable[..., T], time_threshold: float = 1) -> Callable[..., Any]:
    @contextmanager
    def decorating_context(func: Callable[..., T], *args, **kwargs):
        start = time.perf_counter()
        try:
            yield args, kwargs
        except Exception as e:
            raise e
        finally:
            if time_threshold <= 0:
                return
            end = time.perf_counter()
            total = end - start
            if total >= time_threshold:
                print(f'{func.__name__} took {total:.2} second(s) args {args}, kwargs {kwargs}')

    return decorate_sync_async(decorating_context, func)


@decorate_auto_use_params
def retry(func: Callable[..., T], tries: int = 1, delay: Union[int, float] = 1, factor: Union[int, float] = 2) -> Callable[..., T]:
    _tries, _delay = tries, delay
    _tries += 1  # ensure we call func at least once

    if asyncio.iscoroutinefunction(func):
        async def decorated(*args, **kwargs):
            nonlocal _tries, _delay
            while _tries > 0:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    _tries -= 1
                    if _tries == 0:
                        raise e
                    time.sleep(_delay)
                    _delay *= factor

    else:
        def decorated(*args, **kwargs):
            nonlocal _tries, _delay
            while _tries > 0:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    _tries -= 1
                    if _tries == 0:
                        raise e
                    time.sleep(_delay)
                    _delay *= factor
            return func(*args, **kwargs)

    return functools.wraps(func)(decorated)
