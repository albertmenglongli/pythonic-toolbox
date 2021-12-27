def dict_until(obj, keys: list, terminate=lambda v: v is not None, default=None):
    from .list_utils import until
    # default is for value
    val = default
    key = until(keys, lambda k: terminate(obj.get(k, None)), None)
    if key is not None:
        val = obj[key]
    return val
