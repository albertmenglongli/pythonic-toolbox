from collections import deque
from inspect import getmembers, isfunction, getsource
from operator import itemgetter
from pathlib import Path
import subprocess
from typing import List, Optional, Dict, DefaultDict
import re

import funcy

NEW_LINE = '\n'
SPACE = ' '
SHARP = '#'
THREE_BACKTICKS = '```'

MODULE_INTRODUCTIONS: Dict[str, str] = {
    'decorators': (
        'The `decorators` demos highlight reusable wrappers that harden function '
        'interfaces, making call sites more forgiving and resilient to transient '
        'failures.'
    ),
    'deque_utils': (
        '`deque_utils` focuses on ergonomic helpers for Python\'s double-ended '
        'queues, emphasizing efficient mutation patterns.'
    ),
    'dict_utils': (
        'The `dict_utils` section collects richer dictionary abstractions and '
        'traversal helpers for working with nested mappings.'
    ),
    'functional_utils': (
        '`functional_utils` gathers lightweight functional-programming inspired '
        'helpers that compose common iterable transformations.'
    ),
    'list_utils': (
        'Utilities in `list_utils` provide expressive patterns for curation, '
        'ordering, and restructuring of list data.'
    ),
    'string_utils': (
        'The `string_utils` module streamlines templating and value substitution '
        'when building dynamic strings.'
    ),
    'context': (
        '`context` demonstrates context managers that gracefully gate execution '
        'paths based on runtime conditions.'
    ),
}

FUNCTION_INTRODUCTIONS: Dict[str, Dict[str, str]] = {
    'decorators': {
        'ignore_unexpected_kwargs': (
            'Use `ignore_unexpected_kwargs` to accept forgiving keyword arguments '
            'without altering core logic or signatures.'
        ),
        'retry': (
            '`retry` wraps callables with configurable retry logic so transient '
            'errors can be retried transparently.'
        ),
    },
    'deque_utils': {
        'deque_pop_any': (
            '`deque_pop_any` removes the first matching element from a deque while '
            'preserving O(n) traversal semantics.'
        ),
        'deque_split': (
            '`deque_split` partitions a deque into multiple deques based on a '
            'predicate, keeping operations efficient for queue-like workloads.'
        ),
    },
    'dict_utils': {
        'DictObj': (
            '`DictObj` exposes dictionary keys as attributes, enabling dot-style '
            'access in dynamic data structures.'
        ),
        'FinalDictObj': (
            '`FinalDictObj` freezes dictionaries after construction, safeguarding '
            'nested data against accidental mutation.'
        ),
        'RangeKeyDict': (
            '`RangeKeyDict` associates lookup results with numeric ranges, yielding '
            'logarithmic-time queries backed by bisect searches.'
        ),
        'StrKeyIdDict': (
            '`StrKeyIdDict` assigns deterministic integer identifiers to string '
            'keys while maintaining bidirectional lookups.'
        ),
        'collect_leaves': (
            '`collect_leaves` traverses nested dictionaries and gathers terminal '
            'values into a flat structure.'
        ),
        'dict_until': (
            '`dict_until` repeatedly applies mutations to a mapping until a '
            'predicate signals completion.'
        ),
        'select_list_of_dicts': (
            '`select_list_of_dicts` filters lists of dictionaries using expressive '
            'selection predicates.'
        ),
        'unique_list_of_dicts': (
            '`unique_list_of_dicts` collapses dictionaries into a unique list based '
            'on configurable identity keys.'
        ),
        'walk_leaves': (
            '`walk_leaves` yields a generator over nested key paths and leaf values '
            'for introspection-heavy workflows.'
        ),
    },
    'functional_utils': {
        'filter_multi': (
            '`filter_multi` composes multiple predicates for iterative filtering, '
            'with `lfilter_multi` providing a list materialization helper.'
        ),
    },
    'list_utils': {
        'filter_allowable': (
            '`filter_allowable` retains items that match allowable values, whether '
            'they are literal matches or resolved dynamically.'
        ),
        'sort_with_custom_orders': (
            '`sort_with_custom_orders` sorts sequences according to bespoke '
            'priority orders or fallback comparators.'
        ),
        'unpack_list': (
            '`unpack_list` unpacks nested iterables into positional variables with '
            'clear error reporting.'
        ),
        'until': (
            '`until` iterates through data until a stopping condition is met, '
            'mirroring familiar functional-programming patterns.'
        ),
    },
    'string_utils': {
        'substitute_string_template_dict': (
            '`substitute_string_template_dict` safely fills placeholders in string '
            'templates using dictionary-based parameters.'
        ),
    },
    'context': {
        'SkipContext': (
            '`SkipContext` conditionally suppresses execution within a context '
            'manager, ideal for pre-emptive locking or runtime flags.'
        ),
    },
}

URL_PREFIX = "https://github.com/albertmenglongli/pythonic-toolbox/actions/workflows"
BADGE_SUFFIX = "badge.svg?branch=master"

WORKFLOW_CODEQL_LINK = f"{URL_PREFIX}/codeql-analysis.yml"
WORKFLOW_TEST_LINK = f"{URL_PREFIX}/tests-python-versions.yml"
WEBSITE_SNYK_LINK = "https://snyk.io/test/github/albertmenglongli/pythonic-toolbox"
DOWNLOAD_STREAM_LINK = "https://pypistats.org/packages/pythonic-toolbox"

BADGE_CODEQL_LINK = f"{WORKFLOW_CODEQL_LINK}/{BADGE_SUFFIX}"
BADGE_TEST_LINK = f"{WORKFLOW_TEST_LINK}/{BADGE_SUFFIX}"
BADGE_SNYK_LINK = "https://snyk.io/test/github/albertmenglongli/pythonic-toolbox/badge.svg"
BADGE_DOWNLOAD_STREAM_LINK = "https://img.shields.io/badge/dynamic/json?url=https://pypistats.org/api/packages/pythonic-toolbox/recent%3Fperiod%3Dmonth&query=$.data.last_month&label=downloads&suffix=%2Fmonth&cacheSeconds=86400"

TITLE = (f"""# Pythonic toolbox

> README.md is auto generated by the script **tests/generate_readme_markdown.py** from testing files,
>
> **DO NOT EDIT DIRECTLY!**   ;)

```bash
python3 tests/generate_readme_markdown.py
```


## Introduction

A python3.6+ toolbox with multi useful utils, functions, decorators in pythonic way, and is fully tested from python3.6 to python3.11 .

## Installation

```bash
pip3 install pythonic-toolbox --upgrade
```""")

BADGES = (f"""
[![PyPI version](https://badge.fury.io/py/pythonic-toolbox.svg)](https://badge.fury.io/py/pythonic-toolbox)
[![PyPI downloads/mont]({BADGE_DOWNLOAD_STREAM_LINK})]({DOWNLOAD_STREAM_LINK})
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pythonic-toolbox.svg?style=flat&logo=python&logoColor=yellow&labelColor=5c5c5c)](https://pypi.org/project/pythonic-toolbox)
[![Stability](https://img.shields.io/pypi/status/pythonic-toolbox.svg?style=flat)](https://badge.fury.io/py/pythonic-toolbox)
[![CodeQL Status]({BADGE_CODEQL_LINK})]({WORKFLOW_CODEQL_LINK})
[![Python3.6 Test Status]({BADGE_TEST_LINK})]({WORKFLOW_TEST_LINK})
[![SNYK Status]({BADGE_SNYK_LINK})]({WEBSITE_SNYK_LINK})
""")

DIR_PATH = Path(__file__).resolve().parent
README_PATH = DIR_PATH.parent / 'README.md'

begin_block_pattern = re.compile(r'(?<=begin-block-of-content\[)(.*?)(?=])', re.IGNORECASE)
end_block_pattern = re.compile(r'(?<=end-block-of-content\[)(.*?)(?=])', re.IGNORECASE)
insert_block_pattern = re.compile(r'(?<=insert-block-of-content\[)(.*?)(?=])', re.IGNORECASE)


def get_testing_file_paths_under_current_module() -> List[Path]:
    global DIR_PATH
    file_paths = [x for x in DIR_PATH.iterdir() if not x.is_dir()]
    testing_file_paths = [x for x in file_paths if x.name.startswith('test_')]
    return testing_file_paths


def get_functions_in_pkg(pkg):
    return getmembers(pkg, isfunction)


# remove_prefix is introduced after Python 3.9
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def extract_block_of_contents(file_path) -> DefaultDict[str, List[str]]:
    from collections import defaultdict
    cur_block_content_key: Optional[str] = None
    res = defaultdict(list)
    with open(file_path) as f:
        all_lines = f.readlines()
        all_lines = list(map(lambda s: s.replace('\n', ''), all_lines))

    # validation for block of content' begin end pairs
    stack = []
    for line in all_lines:
        begin_match = funcy.first(begin_block_pattern.findall(line))
        end_match = funcy.first(end_block_pattern.findall(line))

        if not begin_match and not end_match:
            continue

        if begin_match:
            stack.append(begin_match)
            continue

        # for end_match case
        if len(stack) == 1 and stack[-1] == end_match:
            stack.pop()
        else:
            raise RuntimeError(f'begin-block-of-content[{end_match}]/end-block-of-content[{end_match}] not match')

    for line in all_lines:
        begin_match = funcy.first(begin_block_pattern.findall(line))
        end_match = funcy.first(end_block_pattern.findall(line))

        if end_match:
            cur_block_content_key = None
            continue

        if cur_block_content_key is None:
            if begin_match:
                cur_block_content_key = begin_match
                continue
        else:
            res[cur_block_content_key].append(line)

    return res


def main():
    test_file_paths: List[Path] = get_testing_file_paths_under_current_module()
    contents: List[str] = [TITLE, '## Usage']
    title_level = 3

    from pythonic_toolbox.utils.list_utils import sort_with_custom_orders

    if test_file_paths:
        test_file_path_dir = funcy.first(test_file_paths).parent
        suffix_orders = [
            test_file_path_dir / 'test_context',
        ]
        test_file_paths = sort_with_custom_orders(test_file_paths,
                                                  # put these test demos in the end, due to a little complicated
                                                  suffix_orders=suffix_orders,
                                                  key=lambda x: x.stem)

    for testing_file_path in test_file_paths:
        pkg_name = testing_file_path.stem
        pkg_name_without_test_ = remove_prefix(pkg_name, 'test_')
        contents.append(SHARP * title_level + SPACE + pkg_name_without_test_)
        module_intro = MODULE_INTRODUCTIONS.get(pkg_name_without_test_)
        if module_intro:
            contents.append(module_intro)
        pkg = __import__(pkg_name)
        name_func_pairs = get_functions_in_pkg(pkg)
        block_of_contents_map: DefaultDict[str, List[str]] = extract_block_of_contents(testing_file_path)
        for func_name, func in sorted(name_func_pairs, key=itemgetter(0)):
            if not func_name.startswith('test_'):
                continue
            title_level += 1
            func_name_without_test_ = remove_prefix(func_name, 'test_')
            contents.append(SHARP * title_level + SPACE + func_name_without_test_)
            func_intro = FUNCTION_INTRODUCTIONS.get(pkg_name_without_test_, {}).get(func_name_without_test_)
            if func_intro:
                contents.append(func_intro)

            source_code_str = getsource(func)
            source_codes_lines = deque(source_code_str.split('\n'))
            source_codes_lines.popleft()  # remove first line for def function
            source_codes_lines.appendleft(THREE_BACKTICKS + 'python3')
            source_codes_lines.append(THREE_BACKTICKS)
            # de-indent the codes
            source_codes_lines = [remove_prefix(line, SPACE * 4) for line in source_codes_lines]

            final_source_code_lines = []
            for line in source_codes_lines:
                insert_match = funcy.first(insert_block_pattern.findall(line))
                if insert_match:
                    lines_to_insert = block_of_contents_map[insert_match]
                    if not lines_to_insert:
                        raise RuntimeError(f'"{insert_match}" block of content not found '
                                           f'in current file: {testing_file_path}')
                    final_source_code_lines.extend(lines_to_insert)
                else:
                    final_source_code_lines.append(line)

            reformatted_source_code_str = '\n'.join(final_source_code_lines)
            contents.append(reformatted_source_code_str)
            title_level -= 1
    readme_content = (NEW_LINE * 2).join(contents)
    with open(README_PATH, 'w') as f:
        f.write(readme_content)

    try:
        curl_cmd_str = 'markdown-toc  -h 4 -t github -toc "## Table of Contents" README.md'
        subprocess.run(curl_cmd_str, shell=True, universal_newlines=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       cwd=README_PATH.parent, check=True)
    except subprocess.CalledProcessError:
        print(('Failed to generate TOC, please run `markdown-toc` manually. \n'
               'To install markdown-toc, run: \n'
               '\tpip3 install markdown-toc --upgrade'))
        print('README.md is generated without TOC!')
    else:
        print('README.md is generated successfully with TOC!')

    # insert badges

    with open(README_PATH, 'r+') as f:
        lines = f.readlines()
        if len(lines) >= 1:
            lines.insert(1, BADGES)

        # Reset the reader's location (in bytes)
        f.seek(0)

        f.writelines(lines)


if __name__ == '__main__':
    main()
