# Pythonic toolbox

A python3.6+ toolbox with multi useful utils, functions, decorators in pythonic way, and is fully tested from python3.6 to python3.9 .

This **README.md** is **Auto-Generated** from testing files by **generate_readme_markdown.py** .

**DO NOT EDIT DIRECTLY!**

## Installation

```bash
pip install pythonic-toolbox
```

# How to use

### context

#### SkipContext

```python3
import itertools
import pytest

from pythonic_toolbox.utils.context_utils import SkipContext

# Usage: define a class that inherits the SkipContext,
# and takes control of the skip or not logic
class MyWorkStation(SkipContext):

    def __init__(self, week_day: str):
        working_days = {'monday', 'tuesday', 'wednesday', 'thursday', 'friday'}
        weekends = {'saturday', 'sunday'}

        if week_day.lower() not in working_days.union(weekends):
            raise ValueError(f'Invalid weekday {week_day}')

        skip = True if week_day.lower() in weekends else False
        super(MyWorkStation, self).__init__(skip=skip)

seven_week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
logged_opening_days = []
total_working_hours = 0

for cur_week_day in seven_week_days:
    # MyWorkStation will skip the code block when encountering weekends
    with MyWorkStation(week_day=cur_week_day):
        # log this working day
        logged_opening_days.append(cur_week_day)
        # accumulate working hours, 8 hours on each working day
        total_working_hours += 8

# only working days are logged
assert logged_opening_days == ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
assert total_working_hours == 8 * 5

# test basic SkipContext
count_iterator = itertools.count(start=0, step=1)

flg_skip = True
with SkipContext(skip=flg_skip):
    # if skip = True, all codes inside the context will be skipped(not executed)
    next(count_iterator)  # this will not be executed
    assert sum([1, 1]) == 3
    raise Exception('Codes will not be executed')

assert next(count_iterator) == 0  # check previous context is skipped

flg_skip = False
with SkipContext(skip=flg_skip):
    # codes will be executed as normal, if skip = False
    next(count_iterator)  # generate value 1
    assert sum([1, 1]) == 2

assert next(count_iterator) == 2  # check previous context is executed

with pytest.raises(Exception) as exec_info:
    with SkipContext(skip=False):
        # if skip = False, this SkipContextManager is transparent,
        # internal exception will be detected as normal
        raise Exception('MyError')
assert exec_info.value.args[0] == 'MyError'

```

### decorators

#### ignore_unexpected_kwargs

```python3
import pytest

from pythonic_toolbox.decorators.common import ignore_unexpected_kwargs

# Following functions are named under Metasyntactic Variables, like:
# foobar, foo, bar, baz, qux, quux, quuz, corge,
# grault, garply, waldo, fred, plugh, xyzzy, thud

def foo(a, b=0, c=3):
    return a, b, c

dct = {'a': 1, 'b': 2, 'd': 4}
with pytest.raises(TypeError) as __:
    assert foo(**dct) == (1, 2, 3)

wrapped_foo = ignore_unexpected_kwargs(foo)
assert wrapped_foo(**dct) == (1, 2, 3)

assert wrapped_foo(0, 0, 0) == (0, 0, 0)
assert wrapped_foo(a=1, b=2, c=3) == (1, 2, 3)

@ignore_unexpected_kwargs
def bar(*args: int):
    return sum(args)

# should not change original behavior
assert bar(1, 2, 3) == 6
assert bar(1, 2, 3, unexpected='Gotcha') == 6
nums = [1, 2, 3]
assert bar(*nums, unexpected='Gotcha') == 6

@ignore_unexpected_kwargs
def qux(a, b, **kwargs):
    # function with Parameter.VAR_KEYWORD Aka **kwargs
    return a, b, kwargs.get('c', 3), kwargs.get('d', 4)

assert qux(**{'a': 1, 'b': 2, 'd': 4, 'e': 5}) == (1, 2, 3, 4)

class Person:
    @ignore_unexpected_kwargs
    def __init__(self, name, age, sex):
        self.name = name
        self.age = age
        self.sex = sex

params = {
    'name': 'albert',
    'age': 34,
    'sex': 'male',
    'height': '170cm',
}
__ = Person(**params)
__ = Person('albert', 35, 'male', height='170cm')

```

#### retry

```python3
import pytest

from pythonic_toolbox.decorators.common import retry

# use decorator without any arguments, using retry default params
@retry
def func_fail_first_time():
    self = func_fail_first_time
    if not hasattr(self, 'call_times'):
        # set attribute call_times for function, to count call times
        self.call_times = 0
    self.call_times += 1
    if self.call_times == 1:
        raise Exception('Fail when first called')
    return 'ok'

assert func_fail_first_time() == 'ok'
assert func_fail_first_time.call_times == 2

@retry(2, delay=0.1)  # use decorator with customized params
def func_fail_twice():
    self = func_fail_twice
    if not hasattr(self, 'call_times'):
        self.call_times = 0
    self.call_times += 1
    if self.call_times <= 2:
        raise Exception('Fail when called first, second time')
    return 'ok'

assert func_fail_twice() == 'ok'
assert func_fail_twice.call_times == 3

@retry(2, delay=0.1)
def func_fail_three_times():
    self = func_fail_three_times
    if not hasattr(self, 'call_times'):
        self.call_times = 0
    self.call_times += 1
    if self.call_times <= 3:  # 1, 2, 3
        raise Exception('Fail when called first, second, third time')
    return 'ok'

with pytest.raises(Exception) as exec_info:
    func_fail_three_times()
assert func_fail_three_times.call_times == 3
assert exec_info.value.args[0] == 'Fail when called first, second, third time'

import asyncio

@retry(delay=0.1)
async def async_func_fail_first_time():
    self = async_func_fail_first_time
    if not hasattr(self, 'call_times'):
        self.call_times = 0
    self.call_times += 1
    if self.call_times == 1:
        raise Exception('Fail when first called')
    return 'ok'

async def async_main():
    assert await async_func_fail_first_time() == 'ok'
    assert async_func_fail_first_time.call_times == 2

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(async_main())
finally:
    loop.close()

```

### deque_utils

#### deque_pop_any

```python3
import pytest
from collections import deque

from pythonic_toolbox.utils.deque_utils import deque_pop_any

queue = deque([1, 2, 3, 4, 5])
assert deque_pop_any(queue, idx=1) == 2
assert queue == deque([1, 3, 4, 5])

# edge case: same as deque.popleft()
queue = deque([1, 2, 3, 4, 5])
assert deque_pop_any(queue, idx=0) == 1
assert queue == deque([2, 3, 4, 5])

# edge case: same as deque.popright()
queue = deque([1, 2, 3, 4, 5])
assert deque_pop_any(queue, idx=len(queue) - 1) == 5
assert queue == deque([1, 2, 3, 4])

queue = deque([1, 2, 3, 4, 5])
with pytest.raises(IndexError) as exec_info:
    deque_pop_any(queue, idx=102)

```

#### deque_split

```python3
import pytest
from collections import deque

from pythonic_toolbox.utils.deque_utils import deque_split

queue1, queue2 = deque_split(deque([1, 2, 3, 4, 5]), num=3)
assert queue1 == deque([1, 2, 3])
assert queue2 == deque([4, 5])

queue1, queue2 = deque_split(deque([1, 2, 3, 4, 5]), num=0)
assert queue1 == deque([])
assert queue2 == deque([1, 2, 3, 4, 5])

queue1, queue2 = deque_split(deque([1, 2, 3, 4, 5]), num=100)
assert queue1 == deque([1, 2, 3, 4, 5])
assert queue2 == deque([])

with pytest.raises(ValueError) as exec_info:
    deque_split(deque([1, 2, 3, 4, 5]), -1)
assert exec_info.value.args[0] == 'num must be integer: 0 <= num <= sys.maxsize'

```

### dict_utils

#### DictObj

```python3
import pytest

from pythonic_toolbox.utils.dict_utils import DictObj

naive_dct = {
    'key1': 'val1',
    'key2': 'val2',
}

obj = DictObj(naive_dct)

# test basic functional methods like dict
assert len(obj) == 2
# same behavior like ordinary dict according to the python version (FILO for popitem for 3.6+)
assert obj.popitem() == ('key2', 'val2')
assert obj.popitem() == ('key1', 'val1')
with pytest.raises(KeyError) as __:
    obj.popitem()

# a key can be treated like an attribute
# an attribute can be treated like a key
obj.key3 = 'val3'
assert obj.pop('key3', None) == 'val3'
assert obj.pop('key4', None) is None
obj.key5 = 'val5'
del obj.key5
assert obj.pop('key5', None) is None

with pytest.raises(KeyError) as __:
    obj.pop('key5')
with pytest.raises(AttributeError) as __:
    del obj.key5

person_dct = {'name': 'Albert', 'age': '34', 'sex': 'Male', 'languages': ['Chinese', 'English']}

person = DictObj(person_dct)
assert person.to_dict() == person_dct
assert set(person.keys()) == {'name', 'age', 'sex', 'languages'}
assert hasattr(person, 'name') is True
assert person.name == 'Albert'
assert person['name'] == 'Albert'
person.languages.append('Japanese')
assert person.languages == ['Chinese', 'English', 'Japanese']

person.height = '170'
assert person['height'] == '170'
assert 'height' in person
assert 'height' in person.keys()
assert hasattr(person, 'height') is True
del person['height']
assert 'height' not in person
assert 'height' not in person.keys()
person['height'] = '170cm'

person.update({'weight': '50'})
weight_val = person.pop('weight')
assert weight_val == '50'
person.update(DictObj({'weight': '50kg'}))
assert person.weight == '50kg'

expected = {
    'name': 'Albert', 'age': '34', 'sex': 'Male',
    'languages': ['Chinese', 'English', 'Japanese'],  # appended new language
    'height': '170cm',  # new added attribute
    'weight': '50kg',  # new added attribute
}
assert person.to_dict() == expected

repr_expected: str = ("{'name': 'Albert', 'age': '34', 'sex': 'Male', "
                      "'languages': ['Chinese', 'English', 'Japanese'],"
                      " 'height': '170cm', 'weight': '50kg'}")
assert repr(person) == repr_expected

# nested structure will be detected, and changed to DictObj
chessboard_data = {
    'position': [
        [{'name': 'knight'}, {'name': 'pawn'}],
        [{'name': 'pawn'}, {'name': 'queen'}],
    ]
}
chessboard_obj = DictObj(chessboard_data)
assert isinstance(chessboard_obj.position, list)
assert len(chessboard_obj.position) == 2
assert isinstance(chessboard_obj.position[0][0], DictObj)
assert chessboard_obj.position[0][0].name == 'knight'
assert chessboard_obj.position[1][1].name == 'queen'

# params validation
invalid_key_dct = {
    '1abc': '1',  # '1abc' is a string, but not valid identifier for python, cannot be used as attribute
}

# test when dict's key cannot be used as an identifier
with pytest.raises(ValueError) as __:
    __ = DictObj(invalid_key_dct)

```

#### FinalDictObj

```python3
import pytest

from pythonic_toolbox.utils.dict_utils import FinalDictObj

person_dct = {'name': 'Albert', 'age': '34', 'sex': 'Male', 'languages': ['Chinese', 'English']}

fixed_person = FinalDictObj(person_dct)
assert fixed_person.name == 'Albert'

# FINAL means once initialized, you cannot change the key/attribute anymore
with pytest.raises(RuntimeError) as exec_info:
    fixed_person.name = 'Steve'
expected_error_str = 'Cannot modify attribute/item in an already initialized FinalDictObj'
assert exec_info.value.args[0] == expected_error_str

with pytest.raises(RuntimeError) as __:
    fixed_person.popitem()

with pytest.raises(RuntimeError) as __:
    fixed_person.pop('name')

assert isinstance(fixed_person.languages, tuple)
with pytest.raises(AttributeError) as exec_info:
    # list values are changed into tuple to avoid being modified
    fixed_person.languages.append('Japanese')
expected_error_str = "'tuple' object has no attribute 'append'"
assert exec_info.value.args[0] == expected_error_str
assert fixed_person.to_dict() == person_dct

# nested structure will be detected, and changed to FinalDictObj
chessboard_data = {
    'position': [
        [{'name': 'knight'}, {'name': 'pawn'}],
        [{'name': 'pawn'}, {'name': 'queen'}],
    ]
}
chessboard_obj = FinalDictObj(chessboard_data)
assert isinstance(chessboard_obj.position, tuple)
assert isinstance(chessboard_obj.position[0][0], FinalDictObj)
assert chessboard_obj.position[1][1].name == 'queen'
with pytest.raises(RuntimeError) as __:
    chessboard_obj.position[1][1].name = 'knight'

```

#### RangeKeyDict

```python3
import pytest

from pythonic_toolbox.utils.dict_utils import RangeKeyDict

# test normal case
range_key_dict = RangeKeyDict({
    (float('-inf'), 0): 'Negative',
    (0, 60): 'F',  # 0 <= val < 60
    (60, 70): 'D',  # 60 <= val < 70
    (70, 80): 'C',  # 70 <= val < 80
    (80, 90): 'B',  # 80 <= val < 90
    (90, 100): 'A',  # 90 <= val < 100
    (100, 100): 'A+',  # val == 100,
    # 100: 'A+',  # val == 100, same as previous line
})

# Big O of querying is O(log n), n is the number of ranges, due to using bisect inside
assert range_key_dict[-1] == 'Negative'
assert range_key_dict[0] == 'F'
assert range_key_dict[55] == 'F'
assert range_key_dict[60] == 'D'
assert range_key_dict[75] == 'C'
assert range_key_dict[85] == 'B'
assert range_key_dict[95] == 'A'
assert range_key_dict[100] == 'A+'

with pytest.raises(KeyError) as exec_info:
    _ = range_key_dict['95']  # when key is not comparable with other integer keys
assert exec_info.value.args[0] == "KeyError: '95' is not comparable with other keys"

with pytest.raises(KeyError) as exec_info:
    _ = range_key_dict[150]
assert exec_info.value.args[0] == 'KeyError: 150'

assert range_key_dict.get(150, 'N/A') == 'N/A'

# combine range-key and fixed-point key together
range_key_dict = RangeKeyDict({
    0: '0',
    1: '1',
    (10, 100): 'val-between-10-and-100'
})

assert range_key_dict[0] == '0'
assert range_key_dict[1] == '1'
assert range_key_dict[10] == 'val-between-10-and-100'
assert range_key_dict[50] == 'val-between-10-and-100'
assert range_key_dict.get(200, 'N/A') == 'N/A'

# validate input keys types and detect range overlaps(segment intersect)
with pytest.raises(ValueError) as exec_info:
    RangeKeyDict({
        (0, 10): 'val-between-0-and-10',
        (0, 5): 'val-between-0-and-5'
    })
expected_error_msg = ("Duplicated left boundary key 0 detected: "
                      "(0, 10): 'val-between-0-and-10', (0, 5): 'val-between-0-and-5'")
assert exec_info.value.args[0] == expected_error_msg

with pytest.raises(ValueError) as exec_info:
    RangeKeyDict({
        (0, 10): 'val-between-0-and-10',
        (5, 15): 'val-between-5-and-15'
    })
expected_error_msg = ("Overlap detected: "
                      "(0, 10): 'val-between-0-and-10', (5, 15): 'val-between-5-and-15'")
assert exec_info.value.args[0] == expected_error_msg

from typing import Union

from functools import total_ordering

@total_ordering
class Age:
    def __init__(self, val: Union[int, float]):
        if not isinstance(val, (int, float)):
            raise ValueError('Invalid age value')
        self.val = val

    def __le__(self, other):
        return self.val <= other.val

    def __repr__(self):
        return f'Age({repr(self.val)})'

    def __hash__(self):
        return hash(self.val)

age_categories_map = RangeKeyDict({
    (Age(0), Age(2)): 'Baby',
    (Age(2), Age(15)): 'Children',
    (Age(15), Age(25)): 'Youth',
    (Age(25), Age(65)): 'Adults',
    (Age(65), Age(123)): 'Seniors',
})

assert age_categories_map[Age(0.5)] == 'Baby'
assert age_categories_map[Age(12)] == 'Children'
assert age_categories_map[Age(20)] == 'Youth'
assert age_categories_map[Age(35)] == 'Adults'
assert age_categories_map[Age(70)] == 'Seniors'

```

#### collect_leaves

```python3
from pythonic_toolbox.utils.dict_utils import collect_leaves

# a nested dict-like struct
my_dict = {
    'node_1': {
        'node_1_1': {
            'node_1_1_1': 'A',
        },
        'node_1_2': {
            'node_1_2_1': 'B',
            'node_1_2_2': 'C',
            'node_1_2_3': None,
        },
        'node_1_3': [  # dict list
            {
                'node_1_3_1_1': 'D',
                'node_1_3_1_2': 'E',
            },
            {
                'node_1_3_2_1': 'FF',
                'node_1_3_2_2': 'GG',
            }
        ]
    }}

expected = ['A', 'B', 'C', None, 'D', 'E', 'FF', 'GG']
assert collect_leaves(my_dict) == expected

expected = ['A', 'B', 'C', 'D', 'E', 'FF', 'GG']
assert collect_leaves(my_dict, leaf_pred=lambda lf: lf) == expected

assert collect_leaves(my_dict, keypath_pred=lambda kp: len(kp) == 1) == []

expected = ['B', 'C']
assert collect_leaves(my_dict, keypath_pred=lambda kp: kp[-1] in {'node_1_2_1', 'node_1_2_2'}) == expected

expected = ['C']
assert collect_leaves(my_dict, leaf_pred=lambda lf: lf == 'C') == expected
assert collect_leaves(my_dict,
                      keypath_pred=lambda kp: kp[-1] == 'node_1_2_2',
                      leaf_pred=lambda lf: lf == 'C') == expected

assert collect_leaves(my_dict,
                      keypath_pred=lambda kp: kp[-1] == 'node_1_1_1',
                      leaf_pred=lambda lf: lf == 'C') == []

expected = ['D', 'E', 'FF', 'GG']
assert collect_leaves(my_dict,
                      keypath_pred=lambda kp: len(kp) >= 2 and kp[-2] == 'node_1_3') == expected

expected = ['FF', 'GG']
assert collect_leaves(my_dict,
                      keypath_pred=lambda kp: len(kp) >= 2 and kp[-2] == 'node_1_3',
                      leaf_pred=lambda lf: isinstance(lf, str) and len(lf) == 2) == expected

# edge cases
assert collect_leaves([]) == []
assert collect_leaves({}) == []
assert collect_leaves(None) == []

```

#### dict_until

```python3
from pythonic_toolbox.utils.dict_utils import dict_until

data = {'full_name': 'Albert Lee', 'pen_name': None}
assert dict_until(data, keys=['name', 'full_name']) == 'Albert Lee'
assert dict_until(data, keys=['full_name', 'name']) == 'Albert Lee'
assert dict_until(data, keys=['name', 'english_name']) is None
assert dict_until(data, keys=['name', 'english_name'], default='anonymous') == 'anonymous'
# test when pen_name is set None on purpose
assert dict_until(data, keys=['pen_name'], default='anonymous') is None
# test when value with None value is not acceptable
assert dict_until(data, keys=['pen_name'], terminate=lambda x: x is not None, default='anonymous') == 'anonymous'

```

#### select_list_of_dicts

```python3
from pythonic_toolbox.utils.dict_utils import select_list_of_dicts

dict_lst = [
    {'name': 'Tony Stark', 'sex': 'male', 'age': 49, 'alias': 'Iron Man'},
    {'name': 'Peter Parker', 'sex': 'male', 'age': 16, 'alias': 'Spider Man'},
    # another Peter Parker from multiverse
    {'name': 'Peter Parker', 'sex': 'male', 'age': 16, 'alias': 'Spider Man'},
    {'name': 'Carol Danvers', 'sex': 'female', 'alias': 'Captain Marvel'},
    {'name': 'Natasha Romanoff', 'sex': 'female', 'age': 35, 'alias': 'Black Widow'},
]

assert select_list_of_dicts(dict_lst, [lambda d: d['sex'] == 'female']) == [
    {'name': 'Carol Danvers', 'sex': 'female', 'alias': 'Captain Marvel'},
    {'name': 'Natasha Romanoff', 'sex': 'female', 'age': 35, 'alias': 'Black Widow'}]

assert select_list_of_dicts(dict_lst, [lambda d: d['sex'] == 'female'], keys=['name']) == [
    {'name': 'Carol Danvers'}, {'name': 'Natasha Romanoff'}]

# unique is supported for return list
assert select_list_of_dicts(dict_lst, [lambda d: d['sex'] == 'male'], keys=['name', 'age']) == [
    {'name': 'Tony Stark', 'age': 49},
    {'name': 'Peter Parker', 'age': 16},
    {'name': 'Peter Parker', 'age': 16},
]

assert select_list_of_dicts(dict_lst, [lambda d: d['sex'] == 'male'], keys=['name', 'age'], unique=True) == [
    {'name': 'Tony Stark', 'age': 49},
    {'name': 'Peter Parker', 'age': 16}]

# dict keys are ordered as the keys passed-in
assert list(select_list_of_dicts(dict_lst, keys=['name', 'age'], unique=True)[0].keys()) == ['name', 'age']
assert list(select_list_of_dicts(dict_lst, keys=['age', 'name'], unique=True)[0].keys()) == ['age', 'name']

# locate Captain Marvel, with default val for missing key
assert select_list_of_dicts(dict_lst,
                            preds=[lambda d: d['alias'] == 'Captain Marvel'],
                            keys=['name', 'sex', 'age', 'alias'],
                            val_for_missing_key='Unknown')[0]['age'] == 'Unknown'

# edge cases, get the original dict
assert select_list_of_dicts([]) == []
assert select_list_of_dicts(dict_lst) == dict_lst

# new list of dicts is returned, leaving the original list of dicts untouched
black_widow = select_list_of_dicts(dict_lst, [lambda d: d['name'] == 'Natasha Romanoff'])[0]
black_widow['age'] += 1
assert black_widow['age'] == 36
# we don't modify the original dict data, Natasha is always 35 years old
assert select_list_of_dicts(dict_lst, [lambda d: d['name'] == 'Natasha Romanoff'])[0]['age'] == 35

# filter the ones with age info
assert len(select_list_of_dicts(dict_lst, [lambda d: 'age' in d])) == 4
assert len(select_list_of_dicts(dict_lst, [lambda d: 'age' in d], unique=True)) == 3

```

#### unique_list_of_dicts

```python3
from pythonic_toolbox.utils.dict_utils import unique_list_of_dicts

dict_lst = [
    {'name': 'Tony Stark', 'sex': 'male', 'age': 49, 'alias': 'Iron Man'},
    {'name': 'Peter Parker', 'sex': 'male', 'age': 16, 'alias': 'Spider Man'},
    # Peter Parkers from multiverse in same age.
    {'name': 'Peter Parker', 'sex': 'male', 'age': 16, 'alias': 'Spider Man'},
    {'name': 'Peter Parker', 'sex': 'male', 'age': 16, 'alias': 'Spider Man'},
]

# Only one Peter Parker will be kept, for all data are exactly same.
assert unique_list_of_dicts(dict_lst) == [
    {'name': 'Tony Stark', 'sex': 'male', 'age': 49, 'alias': 'Iron Man'},
    {'name': 'Peter Parker', 'sex': 'male', 'age': 16, 'alias': 'Spider Man'},
]

# edge cases
assert unique_list_of_dicts([]) == []

```

#### walk_leaves

```python3
from pythonic_toolbox.utils.dict_utils import walk_leaves

data = {
    'k1': {
        'k1_1': 1,
        'k1_2': 2,
    },
    'k2': 'N/A',  # stands for not available
}

expected = {
    'k1': {
        'k1_1': 2,
        'k1_2': 4,
    },
    'k2': 'N/A',  # stands for not available
}
assert walk_leaves(data) == data  # no transform function provided, just a deepcopy
assert walk_leaves(data, trans_fun=lambda x: x * 2 if isinstance(x, int) else x) == expected

# if inplace is set True, will change data inplace, return nothing
assert walk_leaves(data, trans_fun=lambda x: x * 2 if isinstance(x, int) else x, inplace=True) is None
assert data == expected

data = [{'name': 'lml', 'age': 33}, {'name': 'albert', 'age': 18}]
expected = [{'name': 'lml', 'age': 66}, {'name': 'albert', 'age': 36}]
assert walk_leaves(data, trans_fun=lambda x: x * 2 if isinstance(x, int) else x) == expected
assert walk_leaves(data, trans_fun=lambda x: x * 2 if isinstance(x, int) else x, inplace=True) is None
assert data == expected

# edge cases
assert walk_leaves(None) is None
assert walk_leaves([]) == []
assert walk_leaves({}) == {}
assert walk_leaves(None, inplace=True) is None
assert walk_leaves([], inplace=True) is None
assert walk_leaves({}, inplace=True) is None

```

### functional_utils

#### filter_multi

```python3
from pythonic_toolbox.utils.functional_utils import filter_multi

def is_even(x): return x % 2 == 0
def is_divisible_by_5(x): return x % 5 == 0

# select numbers which are divisible by 2 and 5
assert filter_multi([is_even, is_divisible_by_5], range(1, 30)) == [10, 20]
assert filter_multi([is_even, is_divisible_by_5], [5, 10, 15, 20]) == [10, 20]

from itertools import count, takewhile
# if you want to pass an iterator, make sure the iterator will end/break,
# Note: a bare count(start=0, step=2) will generate number like 0, 2, 4, 6, .... (never ends)
even_numbers_less_than_50 = takewhile(lambda x: x <= 50, count(start=0, step=2))
expected = [0, 10, 20, 30, 40, 50]
assert filter_multi([is_even, is_divisible_by_5], even_numbers_less_than_50) == expected

```

### list_utils

#### sort_with_custom_orders

```python3
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

```

#### until

```python3
from itertools import count
from pythonic_toolbox.utils.list_utils import until

# basic usage
counter = count(1, 2)  # generator of odd numbers: 1, 3, 5, 7 ...
assert until(counter, lambda x: x > 10) == 11

assert until([1, 2, 3], lambda x: x > 10, default=11) == 11

# edge cases
assert until([], default=3) == 3  # nothing provided, return default
assert until(None, lambda x: x > 10, default=11) == 11

```