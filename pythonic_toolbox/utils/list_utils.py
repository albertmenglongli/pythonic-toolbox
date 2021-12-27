from typing import Any, List, Iterable, Union, Optional, Hashable, Callable
from collections import defaultdict
import json


def sort_with_custom_orders(values: List[Any],
                            prefix_orders: Optional[List] = None,
                            suffix_orders: Optional[List] = None,
                            key=None, hash_fun=None, reverse=False) -> List[Hashable]:
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


def until(values: Optional[Union[List[Any], Iterable]],
          terminate: Optional[Callable[[Any], bool]] = None,
          default=None) -> Any:
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


if __name__ == '__main__':
    from itertools import count
    import pytest

    counter = count(1, 2)  # generator of odd numbers: 1, 3, 5, 7 ...
    assert until([], default=3) == 3  # nothing provided, return default
    assert until(counter, lambda x: x > 10) == 11
    assert until([1, 2, 3], lambda x: x > 10, default=11) == 11
    assert until(None, lambda x: x > 10, default=11) == 11

    assert sort_with_custom_orders([]) == []
    assert sort_with_custom_orders([], prefix_orders=[], suffix_orders=[]) == []
    assert sort_with_custom_orders([], prefix_orders=['master']) == []

    values = ['branch2', 'branch1', 'branch3', 'master', 'release']
    expected = ['master', 'release', 'branch1', 'branch2', 'branch3']
    assert sort_with_custom_orders(values, prefix_orders=['master', 'release']) == expected
    assert sort_with_custom_orders(values, prefix_orders=['master', 'release'], reverse=True) == expected[::-1]

    values = [1, 2, 3, 9, 9]
    expected = [9, 9, 1, 2, 3]
    assert sort_with_custom_orders(values, prefix_orders=[9, 8, 7]) == expected

    values = [1, 2, 3, 9]
    expected = [9, 2, 3, 1]
    assert sort_with_custom_orders(values, prefix_orders=[9], suffix_orders=[1]) == expected

    # testing for unshashable values
    values = [[2, 2], [1, 1], [3, 3], [6, 0]]
    expected = [[3, 3], [1, 1], [2, 2], [6, 0]]
    assert sort_with_custom_orders(values, prefix_orders=[[3, 3]], key=lambda x: sum(x)) == expected

    values = [{2: 2}, {1: 1}, {1: 2}]
    expected = [{2: 2}, {1: 1}, {1: 2}]
    assert sort_with_custom_orders(values, prefix_orders=[{2: 2}],
                                   key=lambda data: sum(data.values())) == expected
    assert sort_with_custom_orders(values, prefix_orders=[{2: 2}],
                                   key=lambda data: sum(data.values()), hash_fun=tuple) == expected

    with pytest.raises(ValueError) as exec_info:
        sort_with_custom_orders([1, 2, 3], prefix_orders=[3], suffix_orders=[3])
    assert exec_info.value.args[0] == 'prefix and suffix contains same value'

    with pytest.raises(ValueError) as exec_info:
        sort_with_custom_orders([1, 2, 3], prefix_orders=[1, 1])
    assert exec_info.value.args[0] == 'prefix_orders contains duplicated values'


    class Person:
        def __init__(self, id, name, age):
            self.id = id
            self.name = name
            self.age = age

        def __lt__(self, other: 'Person'):
            return self.age < other.age

        def __eq__(self, other: 'Person'):
            return self.age == other.age

        def __hash__(self):
            return self.id

        def __str__(self):
            return f'Person({self.id}, {self.name}, {self.age})'

        def __repr__(self):
            return str(self)


    Albert = Person(1, 'Albert', 28)
    Alice = Person(2, 'Alice', 26)
    Menglong = Person(3, 'Menglong', 33)

    persons = [Albert, Alice, Menglong]
    expected = [Alice, Albert, Menglong]
    assert sort_with_custom_orders(persons) == expected

    expected = [Menglong, Alice, Albert]
    assert sort_with_custom_orders(persons, prefix_orders=[Menglong, Person(4, 'Anyone', 40)]) == expected
