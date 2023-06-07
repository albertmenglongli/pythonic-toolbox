import json
from collections import defaultdict
from functools import singledispatch
from typing import (List, Iterable, Generator, Union, Optional, Callable,
                    TypeVar, Any, Tuple, DefaultDict, Hashable, overload)

from funcy import first, identity

T = TypeVar("T")
T1 = TypeVar("T1")


def sort_with_custom_orders(values: List[T],
                            prefix_orders: Optional[List[T]] = None,
                            suffix_orders: Optional[List[T]] = None,
                            key: Optional[Callable[[T], Any]] = None,
                            hash_fun: Optional[Callable] = None,
                            reverse: bool = False) -> List[T]:
    class Empty:
        pass

    UNSIGNED = Empty()

    if prefix_orders is None:
        prefix_orders = []

    if suffix_orders is None:
        suffix_orders = []

    if not isinstance(prefix_orders, list):
        raise ValueError('prefix_orders should be a list if provided')

    if not isinstance(suffix_orders, list):
        raise ValueError('suffix_orders should be a list if provided')

    default_hash_fun = json.dumps

    if key is None:
        key = identity

    value_types = set(map(type, values))
    value_types.update(set(map(type, prefix_orders)))
    value_types.update(set(map(type, suffix_orders)))
    if len(value_types) > 1:
        raise ValueError('multi types provided in values, prefix_orders, suffix_orders')

    samples = filter(lambda x: x is not UNSIGNED, [first(values)] + [first(prefix_orders)] + [first(suffix_orders)])
    sample = first(samples)

    if sample is UNSIGNED:
        # nothing provided in values, prefix_orders, suffix_orders
        return []

    is_value_type_hashable = True
    try:
        # judge if value type is hashable on runtime
        {sample: None}
    except TypeError:
        is_value_type_hashable = False

    if is_value_type_hashable:
        _hash_fun = hash_fun or identity
    else:
        if hash_fun is not None:
            _hash_fun = hash_fun
        else:
            _hash_fun = default_hash_fun
    hash_fun = _hash_fun

    prefix_orders = list(prefix_orders)
    prefix_orders_set = set(map(hash_fun, prefix_orders))

    if len(prefix_orders) != len(prefix_orders_set):
        raise ValueError('prefix_orders contains duplicated values')

    suffix_orders = list(suffix_orders)
    suffix_orders_set = set(map(hash_fun, suffix_orders))

    if len(suffix_orders) != len(suffix_orders_set):
        raise ValueError('suffix_orders contains duplicated values')

    if prefix_orders_set.intersection(suffix_orders_set):
        raise ValueError('prefix and suffix contains same value')

    order_map: DefaultDict[Hashable, int] = defaultdict(lambda: 1)
    for idx, item in enumerate(prefix_orders):
        order_map[_hash_fun(key(item))] = idx - len(prefix_orders)

    for idx, item in enumerate(suffix_orders, start=2):
        order_map[_hash_fun(key(item))] = idx

    def key_func(x: T) -> Tuple[int, Any]:
        return order_map[hash_fun(key(x))], key(x)

    sorted_values = sorted(values, key=key_func, reverse=reverse)

    return sorted_values


def until(values: Optional[Union[List[T], Iterable]],
          terminate: Optional[Callable[[T], bool]] = None,
          default: Optional[T] = None,
          max_iter_num: Optional[int] = None,
          ) -> Optional[T]:
    class Empty:
        pass

    UNSIGNED = Empty()

    if isinstance(max_iter_num, int):
        if max_iter_num <= 0:
            raise ValueError('max_iter_num should be positive integer')
    elif max_iter_num is None:
        # will not check max_iter_num
        pass
    else:
        raise ValueError('max_iter_num should be positive integer or None')

    def default_terminate(v: Any) -> bool:
        return v is not UNSIGNED

    if values is None:
        return default

    if terminate is None:
        terminate = default_terminate

    if isinstance(values, (list, Iterable)):
        for idx, value in enumerate(values, start=1):
            if max_iter_num is not None and idx > max_iter_num:
                break
            if terminate(value):
                return value
        else:
            pass
        return default
    else:
        raise ValueError('values type should be list, Iterable')


@overload
def unpack_list(source: List[Any], target_num: int, default: Optional[Any] = None) -> List[Any]:
    pass


@overload
def unpack_list(source: Union[Generator, Iterable, range], target_num: int, default: Optional[Any] = None) -> List[Any]:
    pass


@singledispatch
def unpack_list(source: Union[Generator, Iterable, range], target_num: int, default: Optional[Any] = None) -> List[Any]:
    source_iter = iter(source)
    res = []
    cnt = 0
    try:
        while cnt < target_num:
            tmp = next(source_iter)
            res.append(tmp)
            cnt += 1
    except StopIteration:
        pass

    while cnt < target_num:
        res.append(default)
        cnt += 1

    return res


@unpack_list.register(list)
def _(source: List[Any], target_num: int, default: Optional[Any] = None) -> List[Any]:
    return [*source, *([default] * (target_num - len(source)))] if len(source) < target_num else source[:target_num]


def filter_allowable(candidates: Optional[List[T]] = None,
                     allow_list: Optional[List[T1]] = None,
                     block_list: Optional[List[T1]] = None,
                     key: Optional[Callable[..., T1]] = None) -> Iterable[T]:
    if key is None:
        key = identity
    allow_list = allow_list or set()
    block_list = block_list or set()

    allow_list = set(allow_list)
    block_list = set(block_list)

    if candidates is None:
        candidates = []

    candidates = list(candidates)
    candidates = iter(candidates)

    if block_list:
        candidates = filter(lambda x: key(x) not in block_list, candidates)

    if allow_list:
        candidates = filter(lambda x: key(x) in allow_list, candidates)

    return candidates
