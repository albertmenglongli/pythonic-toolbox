import functools
import inspect
from inspect import Parameter
from typing import Callable, Any


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
