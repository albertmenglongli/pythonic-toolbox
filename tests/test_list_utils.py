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
    from operator import itemgetter
    from typing import List

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

    # tests for unhashable values
    values = [[2, 2], [1, 1], [3, 3], [6, 0]]
    assert sort_with_custom_orders(values, prefix_orders=[[3, 3]]) == [[3, 3], [1, 1], [2, 2], [6, 0]]
    # if "key" is provided, items are sorted in order of key(item)
    # items in prefix_orders/suffix_orders don't need to be one-one correspondence with items to sort
    # sum([6]) == sum([3, 3]) == sum([6, 0])
    assert sort_with_custom_orders(values, prefix_orders=[[6]], key=sum) == [[3, 3], [6, 0], [1, 1], [2, 2]]

    # tests for list of dicts
    values = [{2: 2}, {1: 1}, {1: 2}]
    assert sort_with_custom_orders(values, prefix_orders=[{2: 2}],
                                   key=lambda data: sum(data.values())) == [{2: 2}, {1: 2}, {1: 1}]

    branch_info: List[dict] = [{'branch': 'master', 'commit_id': 'v1.2'}, {'branch': 'release', 'commit_id': 'v1.1'}]
    # Assume that we prefer choosing branch in order: release > master > others (develop, hotfix etc.)
    res = sort_with_custom_orders(branch_info,
                                  prefix_orders=[{'branch': 'release'}, {'branch': 'master'}],
                                  key=itemgetter('branch'))
    expected = [{'branch': 'release', 'commit_id': 'v1.1'}, {'branch': 'master', 'commit_id': 'v1.2'}]
    assert res == expected

    branch_info = [{'branch': 'develop', 'commit_id': 'v1.3'}, {'branch': 'master', 'commit_id': 'v1.2'}]
    res = sort_with_custom_orders(branch_info,
                                  prefix_orders=[{'branch': 'release'}, {'branch': 'master'}],
                                  key=itemgetter('branch'))
    expected = [{'branch': 'master', 'commit_id': 'v1.2'}, {'branch': 'develop', 'commit_id': 'v1.3'}]
    assert res == expected

    # tests for exceptions
    with pytest.raises(ValueError) as exec_info:
        sort_with_custom_orders([1, 2, 3], prefix_orders=[3], suffix_orders=[3])
    assert exec_info.value.args[0] == 'prefix and suffix contains same value'

    with pytest.raises(ValueError) as exec_info:
        sort_with_custom_orders([1, 2, 3], prefix_orders=[1, 1])
    assert exec_info.value.args[0] == 'prefix_orders contains duplicated values'

    # tests for class
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


def test_unpack_list():
    import pytest
    from pythonic_toolbox.utils.list_utils import unpack_list

    first, second, third = unpack_list(['a', 'b', 'c', 'd'], target_num=3)
    assert first == 'a' and second == 'b' and third == 'c'

    first, second, third = unpack_list(['a', 'b'], target_num=3, default=None)
    assert first == 'a' and second == 'b' and third is None

    first, second, third = unpack_list(range(1, 3), target_num=3, default=None)
    assert first == 1 and second == 2 and third is None

    first, second, third = unpack_list([], target_num=3, default=0)
    assert first == second == third == 0

    first, second, *rest = unpack_list(['a', 'b', 'c'], target_num=4, default='x')
    assert first == 'a' and second == 'b' and rest == ['c', 'x']

    # test case for type range
    first, second, third = unpack_list(range(1, 3), target_num=3, default=None)
    assert first == 1 and second == 2 and third is None

    def fib():
        a, b = 0, 1
        while 1:
            yield a
            a, b = b, a + b

    # test case for type generator
    fib_generator = fib()  # generates data like [0, 1, 1, 2, 3, 5, 8, 13, 21 ...]
    first, second, third, *rest = unpack_list(fib_generator, target_num=6)
    assert first == 0 and second == 1 and third == 1
    assert rest == [2, 3, 5]
    seventh, eighth = unpack_list(fib_generator, target_num=2)
    assert seventh == 8 and eighth == 13

    # test edge case, nothing to unpack
    empty = unpack_list([], target_num=0, default=None)
    assert empty == []

    res = unpack_list([], target_num=2, default=None)
    assert res == [None, None]

    empty = unpack_list(['a', 'b'], target_num=0, default=None)
    assert empty == []

    empty = unpack_list(range(0, 0), target_num=0)
    assert empty == []

    empty = unpack_list(iter([]), target_num=0, default=None)
    assert empty == []

    with pytest.raises(ValueError):
        # ValueError: not enough values to unpack (expected 3, got 2)
        first, second, third = unpack_list([1, 2], target_num=2)


def test_filter_allowable():
    from pythonic_toolbox.utils.list_utils import filter_allowable

    fruits = ['apple', 'banana', 'orange']
    vegetables = ['carrot', 'potato', 'tomato']
    meats = ['beef', 'chicken', 'fish']

    foods = fruits + vegetables + meats

    assert list(filter_allowable(foods)) == foods
    assert list(filter_allowable(foods, allow_list=[], block_list=[])) == foods
    assert list(filter_allowable(foods, allow_list=['apple', 'banana', 'blueberry'])) == ['apple', 'banana']
    assert list(filter_allowable(foods, allow_list=[], block_list=foods)) == []
    assert list(filter_allowable(foods, block_list=meats)) == fruits + vegetables
    assert list(filter_allowable(foods, allow_list=['apple'], block_list=[])) == ['apple']
    assert list(filter_allowable(foods, allow_list=['apple'], block_list=['apple'])) == []
    assert list(filter_allowable(foods + ['blueberry'], allow_list=[], block_list=foods)) == ['blueberry']
    assert list(filter_allowable(['blueberry'], allow_list=[], block_list=[])) == ['blueberry']
    assert list(filter_allowable(['blueberry'], allow_list=[], block_list=['apple', 'banana'])) == ['blueberry']
    assert list(filter_allowable(['blueberry'], allow_list=['orange'], block_list=['apple', 'banana'])) == []

    # test cases with parameter key
    assert list(filter_allowable(foods, allow_list=['a', 'b'], key=lambda x: x[0])) == ['apple', 'banana', 'beef']

    # test some basic cases
    assert list(filter_allowable()) == []
    assert list(filter_allowable(candidates=None)) == []
    assert list(filter_allowable(candidates=[])) == []
    assert list(filter_allowable(candidates=[], allow_list=[], block_list=[])) == []
