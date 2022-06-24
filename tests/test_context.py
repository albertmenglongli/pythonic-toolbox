# begin-block-of-content[SkipContext example2]
import time

from pythonic_toolbox.utils.context_utils import SkipContext


def plain_cronjob_increase(ns, lock):
    start = time.time()
    with lock:
        now = time.time()
        if now - start >= 0.5:
            pass
        else:
            ns.cnt += 1
            time.sleep(1)
    return ns.cnt


class PreemptiveLockContext(SkipContext):
    def __init__(self, lock):
        self.start_time = time.perf_counter()
        self.lock = lock
        self.acquired = self.lock.acquire(timeout=0.5)
        skip = not self.acquired
        super(PreemptiveLockContext, self).__init__(skip=skip)

    def __exit__(self, type, value, traceback):
        if self.acquired:
            time.sleep(1)
            self.lock.release()
        if type is None:
            return  # No exception
        else:
            if issubclass(type, self.SkipContentException):
                return True  # Suppress special SkipWithBlockException
            return False


def cronjob_increase(ns, lock):
    # for those who cannot acquire the lock within some time
    # this context block will be skipped, quite simple
    with PreemptiveLockContext(lock):
        ns.cnt += 1
    return ns.cnt


# end-block-of-content[SkipContext example2]

def test_SkipContext():
    import itertools

    import pytest
    from pythonic_toolbox.utils.context_utils import SkipContext

    # Usage: define a class that inherits the SkipContext,
    # and takes control of the skip or not logic
    class MyWorkStation(SkipContext):

        def __init__(self, week_day: str):
            working_days = {'monday', 'tuesday', 'wednesday', 'thursday', 'friday'}
            weekends = {'saturday', 'sunday'}

            if week_day.lower() not in working_days.union(weekends):
                raise ValueError(f'Invalid weekday {week_day}')

            skip = True if week_day.lower() in weekends else False
            super(MyWorkStation, self).__init__(skip=skip)

    seven_week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    logged_opening_days = []
    total_working_hours = 0

    for cur_week_day in seven_week_days:
        # MyWorkStation will skip the code block when encountering weekends
        with MyWorkStation(week_day=cur_week_day):
            # log this working day
            logged_opening_days.append(cur_week_day)
            # accumulate working hours, 8 hours on each working day
            total_working_hours += 8

    # only working days are logged
    assert logged_opening_days == ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    assert total_working_hours == 8 * 5

    # test basic SkipContext
    count_iterator = itertools.count(start=0, step=1)

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

    # another example: ensure there will be only one job, who acquire the lock, run the increase +1

    from multiprocessing import Manager, Pool
    # insert-block-of-content[SkipContext example2], content will be injected here when generating README.md

    manager = Manager()
    lock = manager.Lock()
    ns = manager.Namespace()
    pool = Pool(2)

    ns.cnt = 0
    processes = [pool.apply_async(plain_cronjob_increase, args=(ns, lock)) for __ in range(0, 2)]
    result = [p.get() for p in processes]
    assert result == [1, 1]
    assert ns.cnt == 1

    # reset global cnt=0
    ns.cnt = 0
    processes = [pool.apply_async(cronjob_increase, args=(ns, lock)) for __ in range(0, 2)]
    result = [p.get() for p in processes]
    assert result == [1, 1]
    assert ns.cnt == 1
