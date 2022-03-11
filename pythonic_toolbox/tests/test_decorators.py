def test_ignore_unexpected_kwargs():
    import pytest
    from pythonic_toolbox.decorators.common import ignore_unexpected_kwargs

    # Following functions are named under Metasyntactic Variables, like:
    # foobar, foo, bar, baz, qux, quux, quuz, corge,
    # grault, garply, waldo, fred, plugh, xyzzy, thud

    def foo(a, b=0, c=3):
        return a, b, c

    dct = {'a': 1, 'b': 2, 'd': 4}
    with pytest.raises(TypeError) as __:
        assert foo(**dct) == (1, 2, 3)

    wrapped_foo = ignore_unexpected_kwargs(foo)
    assert wrapped_foo(**dct) == (1, 2, 3)

    assert wrapped_foo(0, 0, 0) == (0, 0, 0)
    assert wrapped_foo(a=1, b=2, c=3) == (1, 2, 3)

    @ignore_unexpected_kwargs
    def bar(*args: int):
        return sum(args)

    # should not change original behavior
    assert bar(1, 2, 3) == 6
    assert bar(1, 2, 3, unexpected='Gotcha') == 6
    nums = [1, 2, 3]
    assert bar(*nums, unexpected='Gotcha') == 6

    @ignore_unexpected_kwargs
    def qux(a, b, **kwargs):
        # function with Parameter.VAR_KEYWORD Aka **kwargs
        return a, b, kwargs.get('c', 3), kwargs.get('d', 4)

    assert qux(**{'a': 1, 'b': 2, 'd': 4, 'e': 5}) == (1, 2, 3, 4)

    class Person:
        @ignore_unexpected_kwargs
        def __init__(self, name, age, sex):
            self.name = name
            self.age = age
            self.sex = sex

    params = {
        'name': 'albert',
        'age': 34,
        'sex': 'male',
        'height': '170cm',
    }
    __ = Person(**params)
    __ = Person('albert', 35, 'male', height='170cm')


def test_retry():
    import pytest
    from pythonic_toolbox.decorators.common import retry

    # use decorator without any arguments, using retry default params
    @retry
    def func_fail_first_time():
        self = func_fail_first_time
        if not hasattr(self, 'call_times'):
            # set attribute call_times for function, to count call times
            self.call_times = 0
        self.call_times += 1
        if self.call_times == 1:
            raise Exception('Fail when first called')
        return 'ok'

    assert func_fail_first_time() == 'ok'
    assert func_fail_first_time.call_times == 2

    @retry(2, delay=0.1)  # use decorator with customized params
    def func_fail_twice():
        self = func_fail_twice
        if not hasattr(self, 'call_times'):
            self.call_times = 0
        self.call_times += 1
        if self.call_times <= 2:
            raise Exception('Fail when called first, second time')
        return 'ok'

    assert func_fail_twice() == 'ok'
    assert func_fail_twice.call_times == 3

    @retry(2, delay=0.1)
    def func_fail_three_times():
        self = func_fail_three_times
        if not hasattr(self, 'call_times'):
            self.call_times = 0
        self.call_times += 1
        if self.call_times <= 3:  # 1, 2, 3
            raise Exception('Fail when called first, second, third time')
        return 'ok'

    with pytest.raises(Exception) as exec_info:
        func_fail_three_times()
    assert func_fail_three_times.call_times == 3
    assert exec_info.value.args[0] == 'Fail when called first, second, third time'

    import asyncio

    @retry(delay=0.1)
    async def async_func_fail_first_time():
        self = async_func_fail_first_time
        if not hasattr(self, 'call_times'):
            self.call_times = 0
        self.call_times += 1
        if self.call_times == 1:
            raise Exception('Fail when first called')
        return 'ok'

    async def async_main():
        assert await async_func_fail_first_time() == 'ok'
        assert async_func_fail_first_time.call_times == 2

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(async_main())
    finally:
        loop.close()
