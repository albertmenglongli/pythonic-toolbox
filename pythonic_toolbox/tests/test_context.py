def test_SkipContext():
    from pythonic_toolbox.utils.context_utils import SkipContext
    import itertools

    count_iterator = itertools.count(start=0, step=1)

    import pytest

    flg_skip = True
    with SkipContext(skip=flg_skip):
        # if skip = True, all codes inside the context will be skipped(not executed)
        next(count_iterator)  # this will not be executed
        assert sum([1, 1]) == 3
        raise Exception('Codes will not be executed')

    assert next(count_iterator) == 0  # check previous context is skipped

    flg_skip = False
    with SkipContext(skip=flg_skip):
        # codes will be executed as normal, if skip = False
        next(count_iterator)  # generate value 1
        assert sum([1, 1]) == 2

    assert next(count_iterator) == 2  # check previous context is executed

    with pytest.raises(Exception) as exec_info:
        with SkipContext(skip=False):
            # if skip = False, this SkipContextManager is transparent,
            # internal exception will be detected as normal
            raise Exception('MyError')
    assert exec_info.value.args[0] == 'MyError'
