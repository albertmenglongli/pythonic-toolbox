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
