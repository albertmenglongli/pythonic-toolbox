def test_dict_until():
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


def test_collect_leaves():
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


def test_select_list_of_dicts():
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


def test_unique_list_of_dicts():
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


def test_walk_leaves():
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


def test_DictObj():
    import pytest

    from pythonic_toolbox.utils.dict_utils import DictObj

    naive_dct = {
        'key1': 'val1',
        'key2': 'val2',
    }

    obj = DictObj(naive_dct)

    # test basic functional methods like dict
    assert len(obj) == 2
    assert bool(obj) is True
    # same behavior like ordinary dict according to the python version (FILO for popitem for 3.6+)
    assert obj.popitem() == ('key2', 'val2')
    assert obj.popitem() == ('key1', 'val1')
    with pytest.raises(KeyError) as __:
        obj.popitem()

    # a key can be treated like an attribute
    # an attribute can be treated like a key
    obj.key3 = 'val3'
    assert obj.pop('key3') == 'val3'
    with pytest.raises(KeyError) as __:
        obj.pop('key4')
    obj.key5 = 'val5'
    del obj.key5
    with pytest.raises(KeyError) as __:
        obj.pop('key5')
    with pytest.raises(AttributeError) as __:
        del obj.key5

    # test deepcopy
    from copy import deepcopy
    obj = DictObj({'languages': ['Chinese', 'English']})
    copied_obj = deepcopy(obj)
    assert copied_obj == obj
    copied_obj.languages = obj.languages + ['Japanese']
    assert obj.languages == ['Chinese', 'English']
    assert copied_obj.languages == ['Chinese', 'English', 'Japanese']
    assert copied_obj != obj

    person_dct = {'name': 'Albert', 'age': '34', 'sex': 'Male', 'languages': ['Chinese', 'English']}

    person = DictObj(person_dct)
    assert DictObj(person_dct) == DictObj(person_dct)
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
    # test comparing instances of DictObj
    assert DictObj(chessboard_data) == DictObj(chessboard_data)
    assert isinstance(chessboard_obj.position, list)
    assert len(chessboard_obj.position) == 2
    assert isinstance(chessboard_obj.position[0][0], DictObj)
    assert chessboard_obj.position[0][0].name == 'knight'
    assert chessboard_obj.position[1][1].name == 'queen'

    # edge case empty DictObj
    empty_dict_obj = DictObj({})
    assert len(empty_dict_obj) == 0
    assert bool(empty_dict_obj) is False

    obj_dict = DictObj({'data': 'oops'})
    assert obj_dict.data == 'oops'

    # params validation
    invalid_key_dct = {
        '1abc': '1',  # '1abc' is a string, but not valid identifier for python, cannot be used as attribute
    }

    # test when dict's key cannot be used as an identifier
    with pytest.raises(ValueError) as __:
        __ = DictObj(invalid_key_dct)


def test_FinalDictObj():
    import pytest
    from typing import cast

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
        cast(list, fixed_person.languages).append('Japanese')
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
    # test comparing instances of FinalDictObj
    assert FinalDictObj(chessboard_data) == FinalDictObj(chessboard_data)
    assert isinstance(chessboard_obj.position, tuple)
    assert isinstance(chessboard_obj.position[0][0], FinalDictObj)
    assert chessboard_obj.position[1][1].name == 'queen'
    with pytest.raises(RuntimeError) as __:
        chessboard_obj.position[1][1].name = 'knight'


def test_RangeKeyDict():
    import pytest

    from pythonic_toolbox.utils.dict_utils import RangeKeyDict

    # test normal case
    range_key_dict: RangeKeyDict[float, str] = RangeKeyDict({
        (float('-inf'), 0): 'Negative',
        (0, 60): 'F',  # 0 <= val < 60
        (60, 70): 'D',  # 60 <= val < 70
        (70, 80): 'C',  # 70 <= val < 80
        (80, 90): 'B',  # 80 <= val < 90
        (90, 100): 'A',  # 90 <= val < 100
        100: 'A+',  # val == 100
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

    # test comparison with other RangeKeyDict
    assert RangeKeyDict({(0, 10): '1'}) == RangeKeyDict({(0, 10): '1'})
    assert RangeKeyDict({(0, 10): '1'}) != RangeKeyDict({(0, 10): '2'})
    assert RangeKeyDict({(0, 10): '1'}) != RangeKeyDict({(0, 1000): '1'})

    with pytest.raises(ValueError):
        # [1, 1) is not a valid range
        # there's no value x satisfy 1 <= x < 1
        RangeKeyDict({(1, 1): '1'})

    with pytest.raises(ValueError):
        # [1, -1) is not a valid range
        RangeKeyDict({(1, -1): '1'})

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


def test_StrKeyIdDict():
    import pytest

    from pythonic_toolbox.utils.dict_utils import StrKeyIdDict

    data = {1: 'a', 2: 'b', '3': 'c'}
    my_dict = StrKeyIdDict(data)

    # usage: value can be accessed by id (str: int-like/uuid-like/whatever) or id (int)
    assert my_dict['1'] == my_dict[1] == 'a'
    assert my_dict.keys() == {'1', '2', '3'}  # all keys are str type
    my_dict['4'] = 'd'
    assert my_dict['4'] == 'd'
    my_dict[4] = 'd'
    assert my_dict['4'] == 'd'
    my_dict.update({4: 'd'})
    assert my_dict['4'] == 'd'

    # test comparing instances of the class
    assert StrKeyIdDict(data) == StrKeyIdDict(data)
    assert StrKeyIdDict(data) != StrKeyIdDict(dict(data, **{'4': 'd'}))
    assert StrKeyIdDict(data) == {'1': 'a', '2': 'b', '3': 'c'}
    assert StrKeyIdDict(data) != {'1': 'a', '2': 'b', '3': 'd'}
    assert StrKeyIdDict(data) != {1: 'a', 2: 'b', 3: 'c'}  # StrKeyIdDict assumes all keys are strings

    # test delete key
    del my_dict[4]
    assert my_dict.keys() == {'1', '2', '3'}  # '4' is not in the dict anymore

    # assign value to an arbitrary string key that is not in the dict
    my_dict.update({'some-uuid': 'something'})
    assert my_dict['some-uuid'] == 'something'

    with pytest.raises(TypeError):
        # key '1', 1 both stands for key '1',
        # so we get duplicated keys when initializing instance, oops!
        my_dict = StrKeyIdDict({'1': 'a', 1: 'A'})

    assert my_dict.get(1) == 'a'
    assert my_dict.get('NotExistKey') is None
    assert my_dict.get('NotExistKey', 'NotExistValue') == 'NotExistValue'

    # test edge cases
    assert StrKeyIdDict() == {}

    # test shallow copy
    my_dict[5] = ['e1', 'e2', 'e3']
    copy_dict = my_dict.copy()
    copy_dict[1] = 'A'
    assert my_dict[1] == 'a'
    my_dict['5'].append('e4')
    assert copy_dict['5'] == ['e1', 'e2', 'e3', 'e4']

    # test deep copy
    from copy import deepcopy

    copy_dict = deepcopy(my_dict)
    my_dict[5].append('e5')
    assert my_dict['5'] == ['e1', 'e2', 'e3', 'e4', 'e5']
    assert copy_dict[5] == ['e1', 'e2', 'e3', 'e4']

    # test constructor
    my_dict = StrKeyIdDict(uuid1='a', uuid2='b')
    assert my_dict['uuid1'] == 'a'

    # test constructor (from keys)
    my_dict = StrKeyIdDict.fromkeys([1, 2, 3], None)
    assert my_dict == {'1': None, '2': None, '3': None}
    # test update and overwrite
    my_dict.update(StrKeyIdDict({1: 'a', 2: 'b', 3: 'c', 4: 'd'}))
    assert my_dict == {'1': 'a', '2': 'b', '3': 'c', '4': 'd'}

    my_dict = StrKeyIdDict([(1, 'a'), (2, 'b'), (3, 'c'), (4, 'd')])
    assert my_dict['1'] == my_dict[1] == 'a'

    # reassign StrKeyIdDict instance to another StrKeyIdDict instance
    my_dict = StrKeyIdDict(my_dict)
    assert my_dict == {'1': 'a', '2': 'b', '3': 'c', '4': 'd'}
    assert dict(my_dict) == {'1': 'a', '2': 'b', '3': 'c', '4': 'd'}

    my_dict = StrKeyIdDict({'data': 'oops', '1': 'a'})
    # test case when key is data, which is a reserved keyword inside StrKeyIdDict
    assert my_dict['data'] == 'oops'
    assert my_dict['1'] == 'a'
