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
                trans_fun: Optional[Callable[[Any], Any]] = None) -> Optional[Union[dict, List]]:
    """
    :param data: data can be nested dict, list
    :param trans_fun: leaf transform function
    :return: data
    """
    if data is None:
        return data
    if not isinstance(data, (dict, list)):
        raise ValueError('data must be dict or list')
    obj = deepcopy(data)
    if trans_fun is None:
        trans_fun = lambda x: x

    def _traverse(_obj: Union[Any]):
        if isinstance(_obj, dict):
            _res = {k: _traverse(v) for k, v in _obj.items()}
        elif isinstance(_obj, list):
            _res = [_traverse(elem) for elem in _obj]
        else:
            # no container, just values (str, int, float, None,  obj etc.)
            _obj = trans_fun(_obj)
            _res = _obj
        return _res

    res = _traverse(obj)
    return res
