import functools
import inspect
import time
from functools import lru_cache, wraps
from inspect import Parameter
from typing import Any, Callable, Optional, Set, List, Union


def ignore_unexpected_kwargs(func: Callable[..., Any]) -> Callable[..., Any]:
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
    def wrapper(*args, **kwargs) -> Any:
        kwargs = filter_kwargs(kwargs)
        return func(*args, **kwargs)

    return wrapper


def retry(tries: int, delay: Union[int, float] = 1, factor: Union[int, float] = 2) -> Callable[..., Any]:
    if factor <= 1:
        raise ValueError("back off factor must be greater than 1")

    if not (isinstance(tries, int) and tries > 0):
        raise ValueError("tries must be positive integer")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _tries, _delay = tries, delay
            _tries += 1  # ensure we call func at least once
            while _tries > 0:
                try:
                    ret = func(*args, **kwargs)
                    return ret
                except Exception as e:
                    _tries -= 1
                    # retried enough and still fail? raise original exception
                    if _tries == 0:
                        raise e
                    time.sleep(_delay)
                    # wait longer after each failure
                    _delay *= factor

        return wrapper

    return decorator
