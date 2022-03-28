def test_until():
    from itertools import count
    from pythonic_toolbox.utils.list_utils import until

    # basic usage
    counter = count(1, 2)  # generator of odd numbers: 1, 3, 5, 7 ...
    assert until(counter, lambda x: x > 10) == 11

    assert until([1, 2, 3], lambda x: x > 10, default=11) == 11

    # edge cases
    assert until([], default=3) == 3  # nothing provided, return default
    assert until(None, lambda x: x > 10, default=11) == 11


def test_sort_with_custom_orders():
    import pytest
    from pythonic_toolbox.utils.list_utils import sort_with_custom_orders

    # basic usage
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

    assert sort_with_custom_orders([]) == []
    assert sort_with_custom_orders([], prefix_orders=[], suffix_orders=[]) == []
    assert sort_with_custom_orders([], prefix_orders=['master']) == []

    # testing for unhashable values
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
