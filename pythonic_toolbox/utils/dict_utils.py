from collections import UserDict
from typing import Any, Callable, Optional, List, Hashable, Union
from copy import deepcopy


def dict_until(obj, keys: list, terminate: Optional[Callable[[Any], bool]] = None, default=None):
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
                   leaf_pred: Optional[Callable[[Any], bool]] = None) -> List[Any]:
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
    __lst_factory = list

    def __init__(self, in_dict: dict):

        in_dict = deepcopy(in_dict)

        if any(map(lambda key: not isinstance(key, str), in_dict.keys())):
            raise ValueError('Only string key dict are allowed for DictObj/FinalDictObj input dict')

        for key, val in in_dict.items():
            if isinstance(val, list):
                lst_factory = object.__getattribute__(self, f'_{self.__class__.__name__}__lst_factory')
                in_dict[key] = lst_factory(self.__class__(x) if isinstance(x, dict) else x for x in val)
            elif isinstance(val, dict):
                in_dict[key] = self.__class__(val)
            else:
                in_dict[key] = val

        super(DictObj, self).__init__(**in_dict)

    def __setitem__(self, key, item):
        if isinstance(item, list):
            lst_factory = object.__getattribute__(self, f'_{self.__class__.__name__}__lst_factory')
            self.data[key] = lst_factory(self.__class__(x) if isinstance(x, dict) else x for x in item)
        elif isinstance(item, dict):
            self.data[key] = self.__class__(item)
        else:
            self.data[key] = item

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
            if isinstance(value, list):
                lst_factory = object.__getattribute__(self, f'_{self.__class__.__name__}__lst_factory')
                if lst_factory == tuple:
                    print('Gotcha')
                data[key] = lst_factory(self.__class__(x) if isinstance(x, dict) else x for x in value)
            elif isinstance(value, dict):
                data[key] = self.__class__(value)
            else:
                data[key] = value

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
        del self[item]

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


class FinalDictObj(DictObj):
    __lst_factory = tuple
    __is_frozen = False

    def __init__(self, in_dict: dict):

        in_dict = deepcopy(in_dict)

        super(FinalDictObj, self).__init__(in_dict)
        self._freeze()

    def _freeze(self):
        self.__is_frozen = True

    def __setitem__(self, key, value):
        """DictObj that cannot change attribute"""
        if self.__is_frozen is True:
            raise RuntimeError(f'Cannot set attribute/item {key} in FinalDictObj')
        super(FinalDictObj, self).__setitem__(key, value)

    def __delitem__(self, key):
        if self.__is_frozen is True:
            raise RuntimeError(f'Cannot del attribute or item {key} in an initialized FinalDictObj')
        super(FinalDictObj, self).__delitem__(key)

    def __setattr__(self, key, value):
        """DictObj that cannot change attribute"""
        if key == '_FinalDictObj__is_frozen' and value is True:
            # __is_frozen can only be assigned once
            object.__setattr__(self, key, value)
        else:
            if self.__is_frozen:
                raise RuntimeError(
                    f"Not allowed to assign attribute {key} with value {value} for an initialized FinalDictObj")

            super(FinalDictObj, self).__setattr__(key, value)

    def __delattr__(self, item):
        if self.__is_frozen is True:
            raise RuntimeError(f'Cannot del attribute or item {item} in an initialized FinalDictObj')
        super(FinalDictObj, self).__delattr__(item)

    def update(self, *args, **kwargs):
        if self.__is_frozen is True:
            raise RuntimeError(f'Update not allowed for an initialized FinalDictObj')
        super(FinalDictObj, self).update(*args, **kwargs)
