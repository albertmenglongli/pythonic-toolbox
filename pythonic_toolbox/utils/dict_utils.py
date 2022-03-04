import functools
from collections import UserDict
from copy import deepcopy
from typing import Any, Callable, Optional, List, Hashable, Union, TypeVar

T = TypeVar("T")


def dict_until(obj, keys: list, terminate: Optional[Callable[[T], bool]] = None, default=None) -> T:
    class Empty:
        pass

    UNSIGNED = Empty()

    if terminate is None:
        terminate = lambda v: v is not UNSIGNED

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

    keypath_pred_comb = lambda x: keypath_pred is None or keypath_pred(x)
    leaf_pred_comb = lambda x: leaf_pred is None or leaf_pred(x)

    def _traverse(_data, keypath=None):
        keypath = keypath or []
        if isinstance(_data, dict):
            return {k: _traverse(v, keypath + [k]) for k, v in _data.items()}
        elif isinstance(_data, list):
            return [_traverse(elem, keypath) for elem in _data]
        else:
            # no container, just values (str, int, float, None, obj etc.)
            if keypath_pred_comb(keypath) and leaf_pred_comb(_data):
                leaves.append(_data)

            return _data

    _traverse(data)
    return leaves


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
            __ = {k: _traverse(v, _obj, k) for k, v in _obj.items()}
        elif isinstance(_obj, list):
            __ = [_traverse(elem, _obj, idx) for idx, elem in enumerate(_obj)]
        else:
            # no container, just values (str, int, float, None,  obj etc.)
            parent[idx] = trans_fun(_obj)

    _traverse(obj)
    return obj if inplace is False else None


class DictObj(UserDict):

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
        self.data[key] = self._create_obj_or_keep(item)

    def popitem(self):
        """
        Override popitem from MutableMapping, make behavior popitem FILO like ordinary dict since 3.6
        """
        return self.data.popitem()

    def __getattribute__(self, item):
        if item == 'data':
            return self.__dict__['data']
        else:
            return super(DictObj, self).__getattribute__(item)

    def __delitem__(self, key):
        del self.data[key]

    def __setattr__(self, key, value):
        """DictObj that cannot change attribute"""
        if key == 'data':
            object.__setattr__(self, 'data', value)
        else:
            data = object.__getattribute__(self, 'data')
            data[key] = self._create_obj_or_keep(value)
            object.__setattr__(self, 'data', data)

    def __getattr__(self, item):
        try:
            data = self.__dict__['data']
            res = data[item]
        except KeyError:
            raise AttributeError(f'AttributeError {item}')
        else:
            return res

    def __delattr__(self, item):
        try:
            del self[item]
        except KeyError as e:
            raise AttributeError

    def to_dict(self):
        result = {}
        for key, item in self.data.items():
            if isinstance(item, (list, tuple)):
                result[key] = [x.to_dict() if isinstance(x, DictObj) else x for x in item]
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
