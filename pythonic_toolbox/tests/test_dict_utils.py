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

    assert collect_leaves([]) == []
    assert collect_leaves({}) == []
    assert collect_leaves(None) == []

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


def test_walk_leaves():
    from pythonic_toolbox.utils.dict_utils import walk_leaves

    assert walk_leaves(None) is None
    assert walk_leaves([]) == []
    assert walk_leaves({}) == {}

    assert walk_leaves(None, inplace=True) is None
    assert walk_leaves([], inplace=True) is None
    assert walk_leaves({}, inplace=True) is None

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
    assert walk_leaves(data) == data
    assert walk_leaves(data, trans_fun=lambda x: x * 2 if isinstance(x, int) else x) == expected
    assert walk_leaves(data, trans_fun=lambda x: x * 2 if isinstance(x, int) else x, inplace=True) is None
    assert data == expected

    data = [{'name': 'lml', 'age': 33}, {'name': 'albert', 'age': 18}]
    expected = [{'name': 'lml', 'age': 66}, {'name': 'albert', 'age': 36}]
    assert walk_leaves(data, trans_fun=lambda x: x * 2 if isinstance(x, int) else x) == expected
    assert walk_leaves(data, trans_fun=lambda x: x * 2 if isinstance(x, int) else x, inplace=True) is None
    assert data == expected


def test_dict_obj():
    from pythonic_toolbox.utils.dict_utils import DictObj

    person_dct = {'name': 'Albert', 'age': '34', 'sex': 'Male', 'languages': ['Chinese', 'English']}

    person = DictObj(person_dct)
    assert person.to_dict() == person_dct
    assert set(person.keys()) == {'name', 'age', 'sex', 'languages'}
    assert person.name == 'Albert'
    assert person['name'] == 'Albert'
    person.languages.append('Japanese')
    assert person.languages == ['Chinese', 'English', 'Japanese']

    person.height = '170'
    assert person['height'] == '170'
    assert 'height' in person
    assert 'height' in person.keys()
    del person['height']
    assert 'height' not in person
    assert 'height' not in person.keys()
    person['height'] = '170cm'

    person.update({'weight': '50'})
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


def test_final_dict_obj():
    import pytest
    from pythonic_toolbox.utils.dict_utils import FinalDictObj

    person_dct = {'name': 'Albert', 'age': '34', 'sex': 'Male', 'languages': ['Chinese', 'English']}

    fixed_person = FinalDictObj(person_dct)
    assert fixed_person.name == 'Albert'

    with pytest.raises(RuntimeError) as exec_info:
        fixed_person.name = 'Steve'
    expected_error_str = 'Not allowed to assign attribute name with value Steve for an initialized FinalDictObj'
    assert exec_info.value.args[0] == expected_error_str

    assert type(fixed_person.languages) == tuple
    with pytest.raises(AttributeError) as exec_info:
        # list values are changed into tuple to avoid being modified
        fixed_person.languages.append('Japanese')
    expected_error_str = "'tuple' object has no attribute 'append'"
    assert exec_info.value.args[0] == expected_error_str
    assert fixed_person.to_dict() == person_dct
