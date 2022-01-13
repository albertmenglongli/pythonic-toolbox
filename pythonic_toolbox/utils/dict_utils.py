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
