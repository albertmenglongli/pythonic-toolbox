import json
from collections import defaultdict
from typing import List, Iterable, Union, Optional, Callable, TypeVar

T = TypeVar("T")


def sort_with_custom_orders(values: List[T],
                            prefix_orders: Optional[List[T]] = None,
                            suffix_orders: Optional[List[T]] = None,
                            key=None, hash_fun=None, reverse=False) -> List[T]:
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

    first = lambda seq: next(iter(seq), UNSIGNED)
    identity = lambda x: x
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
        __ = {sample: sample}
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

    order_map = defaultdict(lambda: 1)
    for idx, item in enumerate(prefix_orders):
        order_map[_hash_fun(item)] = idx - len(prefix_orders)

    for idx, item in enumerate(suffix_orders, start=2):
        order_map[_hash_fun(item)] = idx

    sorted_values = sorted(values, key=lambda x: (order_map[hash_fun(x)], key(x)), reverse=reverse)

    return sorted_values


def until(values: Optional[Union[List[T], Iterable]],
          terminate: Optional[Callable[[T], bool]] = None,
          default=None) -> T:
    class Empty:
        pass

    UNSIGNED = Empty()

    if values is None:
        return default

    if terminate is None:
        terminate = lambda v: v is not UNSIGNED

    if isinstance(values, (list, Iterable)):
        for i in values:
            if terminate(i):
                return i
        else:
            pass
        return default
    else:
        raise ValueError('values type should be list, Iterable')
