from functools import reduce
from typing import List, Callable, TypeVar, Iterator, Sequence

T = TypeVar("T")


def filter_multi(functions: Sequence[Callable[[T], bool]], iterator: Iterator[T]) -> List[T]:
    return list(reduce(lambda s, f: filter(f, s), functions, iterator))
