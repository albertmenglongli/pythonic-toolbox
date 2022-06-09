import re
from collections import deque
from itertools import chain
from string import Template
from typing import Any, List, Set, Dict
import sys
import funcy

re_identifier = re.compile(r"(?<=\$)([_a-zA-Z][_a-zA-Z0-9]*)", re.UNICODE)
re_identifier_with_braces = re.compile(r"(?<=\${)[_a-zA-Z][_a-zA-Z0-9]*(?=})", re.UNICODE)

if sys.version_info >= (3, 9):
    from graphlib import CycleError, TopologicalSorter


    def _topological_sort_static_order(graph) -> List:
        ts = TopologicalSorter(graph)
        res = list(ts.static_order())
        return res
else:
    class CycleError(ValueError):
        pass


    def _topological_sort_static_order(graph) -> List:
        gray, black = 0, 1
        order, enter, state = deque(), set(graph), {}

        def dfs(node):
            state[node] = gray
            for k in graph.get(node, ()):
                sk = state.get(k, None)
                if sk == gray:
                    raise CycleError
                if sk == black:
                    continue
                enter.discard(k)
                dfs(k)
            order.appendleft(node)
            state[node] = black

        while enter:
            dfs(enter.pop())
        return list(order)[::-1]


def substitute_string_template_dict(string_template_dict: Dict[str, Any],
                                    *variables_holders: object,
                                    **kwargs) -> dict:
    """
    update and get fill all values in order of user_defined / variables_list[0] / variables_list[1] / ...
    """
    from pythonic_toolbox.utils.list_utils import until
    from pythonic_toolbox.utils.dict_utils import DictObj

    UNASSIGNED = object()

    invalid_keys = list()
    for key in string_template_dict.keys():
        if not isinstance(key, str) or not key.isidentifier():
            invalid_keys.append(key)

    if invalid_keys:
        raise ValueError(
            f'All keys in string_template_dict should be string which can be used as identifier, '
            f'but found: {",".join(map(repr, invalid_keys))}')

    def extract_identifiers(tpl_str) -> Set[str]:
        global re_identifier, re_identifier_with_braces
        res = set()
        if isinstance(tpl_str, str):
            res = set(re_identifier.findall(tpl_str) + re_identifier_with_braces.findall(tpl_str))
        return res

    variables_holders = funcy.lkeep([DictObj(v) if isinstance(v, dict) else v for v in variables_holders] +
                                    [DictObj(kwargs)])
    identifier_value_map = dict()
    identifier_dependency_graph = {item[0]: extract_identifiers(item[1])
                                   for item in string_template_dict.items()}

    top_sorted_identifiers = _topological_sort_static_order(identifier_dependency_graph)

    for identifier in top_sorted_identifiers:
        if identifier in string_template_dict.keys():
            template = string_template_dict[identifier]
            depending_identifiers = identifier_dependency_graph[identifier]

            if not depending_identifiers:
                # raw value/string containing no identifiers
                value = template
            else:
                tmp_params = {}  # store depending-identifier, value dict
                for dep_identifier in depending_identifiers:
                    dep_identifier_value = until(
                        chain([identifier_value_map.get(dep_identifier, UNASSIGNED)],
                              (getattr(variable, dep_identifier, UNASSIGNED) for variable in variables_holders)),
                        terminate=lambda x: x is not UNASSIGNED, default=UNASSIGNED)
                    if dep_identifier_value is UNASSIGNED:
                        raise ValueError('Value for identifier "%s" not provided!' % dep_identifier)
                    else:
                        # assign value for the dependent identifier
                        tmp_params[dep_identifier] = dep_identifier_value
                value = Template(template).substitute(**tmp_params)

            identifier_value_map[identifier] = value

    # generate final result based on identifier_value_map
    rest_dict = funcy.project(identifier_value_map, string_template_dict.keys())
    return rest_dict
