def test_substitute_string_template_dict():
    from unittest.mock import patch, PropertyMock

    import pytest
    from pythonic_toolbox.utils.string_utils import substitute_string_template_dict, CycleError

    # simple usage
    # both $variable ${variable} declarations are supported in string template format
    str_template_dict = {
        'greeting': 'Good Morning, Everyone!',
        'first_name': 'Albert',
        'last_name': 'Lee',
        'full_name': '$first_name $last_name',
        'age': 34,
        'speech': '$greeting, I am $full_name, a ${age}-year-old programmer, very glad to meet you!'
    }
    output_dict = substitute_string_template_dict(str_template_dict)
    assert output_dict['full_name'] == 'Albert Lee'
    expected_speech = 'Good Morning, Everyone!, I am Albert Lee, a 34-year-old programmer, very glad to meet you!'
    assert output_dict['speech'] == expected_speech

    # complex usage, with dynamic values, and multi value-providing holders
    str_template_dict = {
        'first_name': 'Daenerys',
        'last_name': 'Targaryen',
        'nick_name': 'Dany',
        'full_name': '$first_name $last_name',
        'speech': "$nick_name: I'm $full_name ($title1, $title2, $title3), it's $current_time_str, $greeting!",
    }

    variables_dict = {'title1': 'Queen of Meereen',
                      'title2': 'Mother of Dragons'}

    class DynamicVariables:
        @property
        def current_time_str(self):
            import datetime
            return datetime.datetime.now().strftime("%H:%M:%S")

    class DefaultUnknownTitle:
        """
        A class will always return UnknownTitle, when try to access attribute like
        title1, title2, ..., titleX
        """

        def __getattribute__(self, item):
            if isinstance(item, str) and item.startswith('title') and item[len(item) - 1:].isdigit():
                return 'UnknownTitle'
            return super(DefaultUnknownTitle, self).__getattribute__(item)

    expected_speech = ("Dany: I'm Daenerys Targaryen (Queen of Meereen, Mother of Dragons, UnknownTitle), "
                       "it's 08:00:00, good morning everyone!")

    # using mock to make DynamicVariables().current_time_str always return 08:00:00
    with patch.object(DynamicVariables, 'current_time_str', return_value='08:00:00', new_callable=PropertyMock):
        output_dict = substitute_string_template_dict(str_template_dict, variables_dict, DynamicVariables(),
                                                      DefaultUnknownTitle(),
                                                      greeting='good morning everyone')
        assert output_dict['speech'] == expected_speech

    # edge cases
    assert substitute_string_template_dict({}) == {}

    # cycle detection
    str_template_dict = {
        'variable_a': 'Hello $variable_b',  # variable_a depends on variable_b
        'variable_b': 'Hello $variable_a',  # variable_b depends on variable_a, it's a cycle!
    }

    with pytest.raises(CycleError) as exec_info:
        substitute_string_template_dict(str_template_dict)
