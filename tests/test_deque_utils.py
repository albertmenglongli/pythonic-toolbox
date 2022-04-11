def test_deque_split():
    import pytest
    from collections import deque

    from pythonic_toolbox.utils.deque_utils import deque_split

    queue1, queue2 = deque_split(deque([1, 2, 3, 4, 5]), num=3)
    assert queue1 == deque([1, 2, 3])
    assert queue2 == deque([4, 5])

    queue1, queue2 = deque_split(deque([1, 2, 3, 4, 5]), num=0)
    assert queue1 == deque([])
    assert queue2 == deque([1, 2, 3, 4, 5])

    queue1, queue2 = deque_split(deque([1, 2, 3, 4, 5]), num=100)
    assert queue1 == deque([1, 2, 3, 4, 5])
    assert queue2 == deque([])

    with pytest.raises(ValueError) as exec_info:
        deque_split(deque([1, 2, 3, 4, 5]), -1)
    assert exec_info.value.args[0] == 'num must be integer: 0 <= num <= sys.maxsize'


def test_deque_pop_any():
    import pytest
    from collections import deque

    from pythonic_toolbox.utils.deque_utils import deque_pop_any

    queue = deque([1, 2, 3, 4, 5])
    assert deque_pop_any(queue, idx=1) == 2
    assert queue == deque([1, 3, 4, 5])

    # edge case: same as deque.popleft()
    queue = deque([1, 2, 3, 4, 5])
    assert deque_pop_any(queue, idx=0) == 1
    assert queue == deque([2, 3, 4, 5])

    # edge case: same as deque.popright()
    queue = deque([1, 2, 3, 4, 5])
    assert deque_pop_any(queue, idx=len(queue) - 1) == 5
    assert queue == deque([1, 2, 3, 4])

    queue = deque([1, 2, 3, 4, 5])
    with pytest.raises(IndexError) as exec_info:
        deque_pop_any(queue, idx=102)
