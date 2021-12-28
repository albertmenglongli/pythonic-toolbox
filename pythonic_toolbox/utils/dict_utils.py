from typing import Any, Callable, Optional, List, Hashable, Union


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


def collect_leaves(data: Union[dict, List], keypath_pred: Optional[Callable[[List[Hashable]], bool]] = None,
                   leaf_pred: Optional[Callable[[Any], bool]] = None) -> List[Any]:
    leaves = list()
    leaf_pred_comb = lambda x: leaf_pred is None or leaf_pred(x)
    keypath_pred_comb = lambda x: keypath_pred is None or keypath_pred(x)

    def _traverse(_data, keypath=None):
        keypath = keypath or []
        if isinstance(_data, dict):
            return {k: _traverse(v, keypath + [k]) for k, v in _data.items()}
        elif isinstance(_data, list):
            return [_traverse(elem, keypath) for elem in _data]
        else:
            # no container, just values (str, int, float, null, obj etc.)
            if keypath_pred_comb(keypath) and leaf_pred_comb(_data):
                leaves.append(_data)

            return _data

    _traverse(data)
    return leaves

