import functools
import numbers
from bisect import bisect_left
from collections import UserDict, namedtuple
from collections.abc import MutableMapping
from copy import deepcopy
from operator import attrgetter
from typing import Any, Callable, Dict, Hashable, Iterator, List, Optional, Tuple, TypeVar, Union, Sequence

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def dict_until(obj, keys: list, terminate: Optional[Callable[[T], bool]] = None, default=None) -> T:
    class Empty:
        pass

    UNSIGNED = Empty()

    if terminate is None:
        def terminate(v): return v is not UNSIGNED

    from pythonic_toolbox.utils.list_utils import until

    # default is for value
    val = default
    key = until(keys, lambda k: terminate(obj.get(k, UNSIGNED)), default=UNSIGNED)
    if key is not UNSIGNED:
        val = obj[key]
    return val


def collect_leaves(data: Optional[Union[dict, List]] = None,
                   keypath_pred: Optional[Callable[[List[Hashable]], bool]] = None,
                   leaf_pred: Optional[Callable[[T], bool]] = None) -> List[T]:
    leaves = list()
    if not data:
        return leaves

    def keypath_pred_comb(x):
        return keypath_pred is None or keypath_pred(x)

    def leaf_pred_comb(x):
        return leaf_pred is None or leaf_pred(x)

    def _traverse(_user_dict_hidden_data, keypath=None):
        keypath = keypath or []
        if isinstance(_user_dict_hidden_data, dict):
            return {k: _traverse(v, keypath + [k]) for k, v in _user_dict_hidden_data.items()}
        elif isinstance(_user_dict_hidden_data, list):
            return [_traverse(elem, keypath) for elem in _user_dict_hidden_data]
        else:
            # no container, just values (str, int, float, None, obj etc.)
            if keypath_pred_comb(keypath) and leaf_pred_comb(_user_dict_hidden_data):
                leaves.append(_user_dict_hidden_data)

            return _user_dict_hidden_data

    _traverse(data)
    return leaves


def select_list_of_dicts(dict_lst: List[dict],
                         preds: Optional[Iterator[Callable[[dict], bool]]] = None,
                         keys: Optional[Hashable] = None,
                         unique=False, val_for_missing_key=None) -> List[dict]:
    """ Select part of the dict collections."""

    from funcy import rpartial, project, all_fn

    preds = preds or []
    keys = keys or []

    dict_lst = deepcopy(dict_lst)
    res: Union[List[dict], Iterator[dict]] = dict_lst

    if preds:
        res = filter(all_fn(*preds), dict_lst)

    if keys:
        # select target keys
        res = map(rpartial(project, keys=keys), res)
        # re-order dict keys and fill value for missing key
        res = [{k: dct.get(k, val_for_missing_key) for k in keys} for dct in res]

    if unique is True:
        res = unique_list_of_dicts(res)

    return list(res)


def unique_list_of_dicts(dict_list: List[dict]) -> List[dict]:
    unique_res: List[dict] = []
    items_tuple_set = set()
    for d in dict_list:
        items_tuple = tuple(d.items())
        if items_tuple not in items_tuple_set:
            unique_res.append(deepcopy(d))
            items_tuple_set.add(items_tuple)
    return unique_res


def walk_leaves(data: Optional[Union[dict, List]] = None,
                trans_fun: Optional[Callable[[Any], Any]] = None,
                inplace=False) -> Optional[Union[dict, List]]:
    """
    :param data: data can be nested dict, list
    :param trans_fun: leaf transform function
    :param inplace: change values in place or not
    :return: replace data with transformed leaves, will return None in transform inplace
    """
    if data is None:
        return data
    if not isinstance(data, (dict, list)):
        raise ValueError('data must be dict or list')

    if inplace is True:
        obj = data
    else:
        # won't touch the original data
        obj = deepcopy(data)

    if trans_fun is None:
        return obj if inplace is False else None

    def _traverse(_obj, parent: Optional[Union[dict, list]] = None,
                  idx: Optional[Union[int, Hashable]] = None) -> None:
        """
        This inner function transform leaves value inplace
        """
        if isinstance(_obj, dict):
            for k, v in _obj.items():
                _traverse(v, _obj, k)
        elif isinstance(_obj, list):
            for idx, elem in enumerate(_obj):
                _traverse(elem, _obj, idx)
        else:
            # no container, just values (str, int, float, None,  obj etc.)
            parent[idx] = trans_fun(_obj)

    _traverse(obj)
    return obj if inplace is False else None


class MyUserDict(MutableMapping):

    # Start by filling-out the abstract methods
    def __init__(*args, **kwargs):
        if not args:
            raise TypeError("descriptor '__init__' of 'UserDict' object "
                            "needs an argument")
        self, *args = args
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        if args:
            dict = args[0]
        elif 'dict' in kwargs:
            dict = kwargs.pop('dict')
            import warnings
            warnings.warn("Passing 'dict' as keyword argument is deprecated",
                          DeprecationWarning, stacklevel=2)
        else:
            dict = None
        self._user_dict_hidden_data = {}
        if dict is not None:
            self.update(dict)
        if len(kwargs):
            self.update(kwargs)

    def __len__(self):
        return len(self._user_dict_hidden_data)

    def __getitem__(self, key):
        if key in self._user_dict_hidden_data:
            return self._user_dict_hidden_data[key]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __setitem__(self, key, item):
        self._user_dict_hidden_data[key] = item

    def __delitem__(self, key):
        del self._user_dict_hidden_data[key]

    def __iter__(self):
        return iter(self._user_dict_hidden_data)

    # Modify __contains__ to work correctly when __missing__ is present
    def __contains__(self, key):
        return key in self._user_dict_hidden_data

    # Now, add the methods in dicts but not in MutableMapping
    def __repr__(self):
        return repr(self._user_dict_hidden_data)

    def copy(self):
        if self.__class__ is UserDict:
            return UserDict(self._user_dict_hidden_data.copy())
        import copy
        data = self._user_dict_hidden_data
        try:
            self._user_dict_hidden_data = {}
            c = copy.copy(self)
        finally:
            self._user_dict_hidden_data = data
        c.update(self)
        return c

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d


class DictObj(MyUserDict):
    def __init__(self, in_dict: dict):

        in_dict = deepcopy(in_dict)

        if any(map(lambda key: not isinstance(key, str) or (isinstance(key, str) and not key.isidentifier()),
                   in_dict.keys())):
            raise ValueError('input dict for DictObj/FinalDictObj must have only string keys,'
                             ' and keys must be valid identifiers')

        for key, val in in_dict.items():
            in_dict[key] = self._create_obj_or_keep(val)

        super(DictObj, self).__init__(**in_dict)

    @classmethod
    def _create_obj_or_keep(cls, data):
        if isinstance(data, dict):
            return cls(data)
        elif isinstance(data, (list, tuple)):
            return list(cls._create_obj_or_keep(x) for x in data)
        else:
            return data

    def __setitem__(self, key, item):
        self._user_dict_hidden_data[key] = self._create_obj_or_keep(item)

    def popitem(self):
        """
        Override popitem from MutableMapping, make behavior popitem FILO like ordinary dict since 3.6
        """
        return self._user_dict_hidden_data.popitem()

    def pop(self, key):
        val = self._user_dict_hidden_data[key]
        del self._user_dict_hidden_data[key]
        return val

    def __getattribute__(self, item):
        if item == '_user_dict_hidden_data':
            return self.__dict__['_user_dict_hidden_data']
        else:
            return super(DictObj, self).__getattribute__(item)

    def __delitem__(self, key):
        del self._user_dict_hidden_data[key]

    def __setattr__(self, key, value):
        """DictObj that can change attribute"""
        if key == '_user_dict_hidden_data':
            object.__setattr__(self, '_user_dict_hidden_data', value)
        else:
            data = object.__getattribute__(self, '_user_dict_hidden_data')
            data[key] = self._create_obj_or_keep(value)
            object.__setattr__(self, '_user_dict_hidden_data', data)

    def __getattr__(self, item):
        try:
            data = self.__dict__['_user_dict_hidden_data']
            res = data[item]
        except KeyError:
            raise AttributeError(f'AttributeError {item}')
        else:
            return res

    def __delattr__(self, item):
        try:
            del self[item]
        except KeyError:
            raise AttributeError

    def to_dict(self):
        result = {}
        for key, item in self._user_dict_hidden_data.items():
            if isinstance(item, (list, tuple)):
                result[key] = [x.to_dict() if hasattr(x, 'to_dict') and callable(getattr(x, 'to_dict')) else x
                               for x in item]
            elif isinstance(item, DictObj):
                result[key] = item.to_dict()
            else:
                result[key] = item
        return result


def _frozen_checker(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._FinalDictObj__is_frozen is True:
            raise RuntimeError(self._FinalDictObj__frozen_err_msg)
        return func(self, *args, **kwargs)

    return wrapper


class FinalDictObj(DictObj):
    __is_frozen = False
    __frozen_err_msg = 'Cannot modify attribute/item in an already initialized FinalDictObj'

    def __init__(self, in_dict: dict):

        in_dict = deepcopy(in_dict)

        super(FinalDictObj, self).__init__(in_dict)
        self._freeze()

    @classmethod
    def _create_obj_or_keep(cls, data):
        if isinstance(data, dict):
            return cls(data)
        elif isinstance(data, (list, tuple)):
            return tuple(cls._create_obj_or_keep(x) for x in data)
        else:
            return data

    def _freeze(self):
        self.__is_frozen = True

    @_frozen_checker
    def __setitem__(self, key, value):
        """DictObj that cannot change attribute"""
        super(FinalDictObj, self).__setitem__(key, value)

    @_frozen_checker
    def __delitem__(self, key):
        super(FinalDictObj, self).__delitem__(key)

    @_frozen_checker
    def popitem(self):
        return super(FinalDictObj, self).popitem()

    @_frozen_checker
    def pop(self, key):
        return super(FinalDictObj, self).pop(key)

    def __setattr__(self, key, value):
        """DictObj that cannot change attribute"""
        if key == '_FinalDictObj__is_frozen':
            if value is True:
                # __is_frozen can only be assigned as True
                object.__setattr__(self, '_FinalDictObj__is_frozen', True)
            else:
                raise RuntimeError('__is_frozen can only be assigned as True')
        else:
            if self.__is_frozen:
                raise RuntimeError(self.__frozen_err_msg)

            super(FinalDictObj, self).__setattr__(key, value)

    @_frozen_checker
    def __delattr__(self, item):
        super(FinalDictObj, self).__delattr__(item)

    @_frozen_checker
    def update(self, *args, **kwargs):
        super(FinalDictObj, self).update(*args, **kwargs)


class RangeKeyDict:
    """
    RangeKeyDict uses tuple of key pairs to present range keys, notice that the range is left-closed/right-open
    [min, max): min <= key < max, Big O of querying is O(log n), n is the number of ranges, due to using bisect inside
    """

    class Segment(namedtuple('Segment', ['begin', 'end', 'val'])):
        def __contains__(self, item):
            return self.begin == item or self.begin < item < self.end

        def __str__(self):
            return f'({repr(self.begin)}, {repr(self.end)}): {repr(self.val)}'

        def __repr__(self):
            return f'RangeKeyDict.Segment(begin={repr(self.begin)}, end={repr(self.end)}, val={repr(self.val)}'

    def __init__(self, input_dict: Dict[Union[Tuple[K, K], K], V]) -> None:
        """keys for input dict must be tuple-like intervals (left-closed, right-open) or single point"""
        # input validation and generate inner-used structures
        single_point_map, left_boundary_map, sorted_segments = self._gen_inner_structures_and_validate_inputs(
            input_dict)

        self._single_point_map = single_point_map
        self._left_boundary_segment_map = left_boundary_map
        self._sorted_segments = sorted_segments

    @staticmethod
    def _gen_inner_structures_and_validate_inputs(input_dict: Dict[Union[Tuple[K, K], K], V]) -> Tuple[
        Dict[K, V], Dict[K, Segment], Sequence[Segment]]:
        def validate_boundary_key_type(boundary_key_lst: List[K]):
            if boundary_key_lst:
                if all(map(lambda x: isinstance(x, numbers.Number), boundary_key_lst)):
                    # if all the boundaries are numbers, OK
                    pass
                else:
                    if not all(map(lambda x: isinstance(x, type(boundary_key_lst[0])), boundary_key_lst)):
                        all_types = set(map(type, boundary_key_lst))
                        raise ValueError(
                            f'All the boundaries must be either all numbers '
                            f'or of same type, multi types detected: {[tp.__name__ for tp in all_types]}')
                    else:
                        # one_key = boundary_key_lst[0]
                        # one_key < one_key
                        pass

        def sort_and_validate_segments_overlap(segment_lst: List[RangeKeyDict.Segment]) -> None:
            # keys overlapping validation
            # sort segments inplace by begin value,end value
            segment_lst.sort(key=lambda s: (s.begin, s.end))

            if len(segment_lst) > 0:
                for prev, cur in zip(segment_lst, segment_lst[1:]):
                    if prev.end > cur.begin or prev.begin == prev.end == cur.begin:
                        raise ValueError(f'Overlap detected: {str(prev)}, {str(cur)}')

        boundary_keys: List[K] = list()
        single_point_map: Dict[K, V] = dict()
        left_boundary_key_segment_map: Dict[K, RangeKeyDict.Segment] = dict()
        segments: List[RangeKeyDict.Segment] = list()
        for key, val in input_dict.items():
            if isinstance(key, tuple) and len(key) == 2:
                left_boundary_key, right_boundary_key = key
                try:
                    if (isinstance(left_boundary_key, Hashable) and
                            isinstance(right_boundary_key, Hashable) and
                            (left_boundary_key < right_boundary_key or
                             left_boundary_key == right_boundary_key)):
                        boundary_keys.extend([left_boundary_key, right_boundary_key])
                    else:
                        raise ValueError
                except (TypeError, ValueError):
                    raise ValueError(f'Invalid key for {repr(key)}, '
                                     f'left boundary keys must <= right boundary key, '
                                     f'and both of them must be hashable, have completed comparison methods')
            elif isinstance(key, Hashable):
                single_point_map[key] = val
                boundary_keys.append(key)
                left_boundary_key = right_boundary_key = key
            else:
                raise ValueError(f'Invalid begin/end pairs detected for {repr(key)}')

            segment = RangeKeyDict.Segment(begin=left_boundary_key, end=right_boundary_key, val=val)
            segments.append(segment)
            if left_boundary_key in left_boundary_key_segment_map:
                prev_segment = left_boundary_key_segment_map[left_boundary_key]
                raise ValueError(
                    f'Duplicated left boundary key {repr(left_boundary_key)} detected: '
                    f'{str(prev_segment)}, {str(segment)}')
            else:
                left_boundary_key_segment_map[left_boundary_key] = segment

        validate_boundary_key_type(boundary_keys)
        sort_and_validate_segments_overlap(segments)

        return single_point_map, left_boundary_key_segment_map, segments

    def __getitem__(self, number):
        if number in self._single_point_map:
            return self._single_point_map[number]
        try:
            idx = bisect_left(list(map(attrgetter('begin'), self._sorted_segments)), number)
        except TypeError:
            raise KeyError(f'KeyError: {repr(number)} is not comparable with other keys')
        else:
            if idx == 0:
                if number in self._sorted_segments[idx]:
                    return self._sorted_segments[idx].val
            elif idx == len(self._sorted_segments):
                if number in self._sorted_segments[-1]:
                    return self._sorted_segments[-1].val
            else:
                for target_idx in (idx - 1, idx):
                    if number in self._sorted_segments[target_idx]:
                        return self._sorted_segments[target_idx].val
            raise KeyError(f'KeyError: {repr(number)}')

    def get(self, number, default=None):
        try:
            return self.__getitem__(number)
        except KeyError:
            return default


class StrKeyIdDict(UserDict):
    """
    A dictionary convert all ID keys (string or integer) to string type.
    Int type ID is fast in DB, but when being passed between systems/processes/APIs,
    we convert it to string for dict to avoid being bitten by off-hands ID types problem.
    """

    def __init__(self, *args, **kwargs):
        validated_data = self._validate_input(*args, **kwargs)
        super().__init__(validated_data)

    def _validate_input(self, *args, **kwargs) -> Dict:
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        if args:
            my_dict = args[0]
        elif 'dict' in kwargs:
            my_dict = kwargs.pop('dict')
        else:
            my_dict = {}

        raw_data: Dict = {}
        raw_data.update(my_dict)
        raw_data.update(kwargs)

        valid_data = {}
        for key, val in raw_data.items():
            if not self.is_valid_key(key):
                raise TypeError(
                    f'{repr(key)}: Key for ID must be an integer or a string, but got {type(key)}')
            if str(key) not in valid_data.keys():
                valid_data[str(key)] = val
            else:
                # handle duplicated keys (e.g. '1', 1)
                duplicate_keys = set()
                if str(key) in raw_data.keys():
                    duplicate_keys.add(str(key))
                if int(key) in raw_data.keys():
                    duplicate_keys.add(int(key))
                raise TypeError(f'Duplicated keys: {",".join(map(repr, duplicate_keys))} detected')

        return valid_data

    @classmethod
    def is_valid_key(cls, key):
        return isinstance(key, (int, str))

    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(f'KeyError: {repr(key)}')
        return self[str(key)]

    def __contains__(self, key):
        return str(key) in self.data

    def __setitem__(self, key, value):
        if not self.is_valid_key(key):
            raise TypeError(f'Key must be a string or integer, but got {repr(key)}')
        self.data[str(key)] = value

    def __delitem__(self, key):
        del self.data[str(key)]

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d
