import itertools
from collections import deque
from typing import Deque, Tuple, TypeVar
import sys

T = TypeVar("T")


def deque_split(queue: Deque[T], num: int) -> Tuple[Deque[T], Deque[T]]:
    if not 0 <= num <= sys.maxsize:
        raise ValueError('num must be integer: 0 <= num <= sys.maxsize')
    return deque(itertools.islice(queue, num)), deque(itertools.islice(queue, num, len(queue)))


def deque_pop_any(queue: Deque[T], idx: int) -> T:
    if len(queue) == 0:
        raise IndexError('pop from empty deque')
    if not 0 <= idx <= len(queue) - 1:
        raise IndexError('index out of range')
    queue.rotate(-idx)
    res = queue.popleft()
    queue.rotate(idx)
    return res
