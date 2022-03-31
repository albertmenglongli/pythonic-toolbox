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
