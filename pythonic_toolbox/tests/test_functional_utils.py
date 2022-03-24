def test_filter_multi():
    from pythonic_toolbox.utils.functional_utils import filter_multi

    def is_even(x): return x % 2 == 0
    def is_divisible_by_5(x): return x % 5 == 0

    # select numbers which are divisible by 2 and 5
    assert filter_multi([is_even, is_divisible_by_5], range(1, 30)) == [10, 20]
    assert filter_multi([is_even, is_divisible_by_5], [5, 10, 15, 20]) == [10, 20]

    from itertools import count, takewhile
    # if you want to pass an iterator, make sure the iterator will end/break,
    # Note: a bare count(start=0, step=2) will generate number like 0, 2, 4, 6, .... (never ends)
    even_numbers_less_than_50 = takewhile(lambda x: x <= 50, count(start=0, step=2))
    expected = [0, 10, 20, 30, 40, 50]
    assert filter_multi([is_even, is_divisible_by_5], even_numbers_less_than_50) == expected
