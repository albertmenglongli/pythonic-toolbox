from typing import Any, Callable, Optional


def dict_until(obj, keys: list, terminate: Optional[Callable[[Any], bool]] = None, default=None):
    class Empty:
        pass

    UNSIGNED = Empty()

    if terminate is None:
        terminate = lambda v: v is not UNSIGNED

    from list_utils import until

    # default is for value
    val = default
    key = until(keys, lambda k: terminate(obj.get(k, UNSIGNED)), default=UNSIGNED)
    if key is not UNSIGNED:
        val = obj[key]
    return val


if __name__ == '__main__':
    data = {'full_name': 'Albert Lee', 'pen_name': None}
    assert dict_until(data, keys=['name', 'full_name']) == 'Albert Lee'
    assert dict_until(data, keys=['full_name', 'name']) == 'Albert Lee'
    assert dict_until(data, keys=['name', 'english_name']) is None
    assert dict_until(data, keys=['name', 'english_name'], default='anonymous') == 'anonymous'
    # test when pen_name is set None on purpose
    assert dict_until(data, keys=['pen_name'], default='anonymous') is None
    # test when value with None value is not acceptable
    assert dict_until(data, keys=['pen_name'], terminate=lambda x: x is not None, default='anonymous') == 'anonymous'
