from functools import reduce
from typing import List, Callable, TypeVar, Iterator, Sequence, Union

T = TypeVar("T")


def filter_multi(functions: Sequence[Callable[[T], bool]], items: Union[Sequence[T], Iterator[T]]) -> filter:
    return reduce(lambda s, f: filter(f, s), functions, items)


def lfilter_multi(functions: Sequence[Callable[[T], bool]], items: Union[Sequence[T], Iterator[T]]) -> List[T]:
    return list(filter_multi(functions, items))
