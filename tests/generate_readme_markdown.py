from collections import deque
from inspect import getmembers, isfunction, getsource
from operator import itemgetter
from pathlib import Path
import subprocess
from typing import List

NEW_LINE = '\n'
SPACE = ' '
SHARP = '#'
THREE_BACKTICKS = '```'

URL_PREFIX = "https://github.com/albertmenglongli/pythonic-toolbox/actions/workflows"
BADGE_SUFFIX = "badge.svg?branch=master"

WORKFLOW_TEST_PY36_LINK = f"{URL_PREFIX}/tests-python36.yml"
WORKFLOW_TEST_PY37_LINK = f"{URL_PREFIX}/tests-python37.yml"
WORKFLOW_TEST_PY38_LINK = f"{URL_PREFIX}/tests-python38.yml"
WORKFLOW_TEST_PY39_LINK = f"{URL_PREFIX}/tests-python39.yml"
WORKFLOW_TEST_PY310_LINK = f"{URL_PREFIX}/tests-python310.yml"

BADGE_TEST_PY36_LINK = f"{WORKFLOW_TEST_PY36_LINK}/{BADGE_SUFFIX}"
BADGE_TEST_PY37_LINK = f"{WORKFLOW_TEST_PY37_LINK}/{BADGE_SUFFIX}"
BADGE_TEST_PY38_LINK = f"{WORKFLOW_TEST_PY38_LINK}/{BADGE_SUFFIX}"
BADGE_TEST_PY39_LINK = f"{WORKFLOW_TEST_PY39_LINK}/{BADGE_SUFFIX}"
BADGE_TEST_PY310_LINK = f"{WORKFLOW_TEST_PY310_LINK}/{BADGE_SUFFIX}"

TITLE = (f"""# Pythonic toolbox

> README.md is auto generated by the script **tests/generate_readme_markdown.py** from testing files,
>
> **DO NOT EDIT DIRECTLY!**   ;)

```bash
python3 tests/generate_readme_markdown.py
```


## Introduction

A python3.6+ toolbox with multi useful utils, functions, decorators in pythonic way, and is fully tested from python3.6 to python3.10 .


| Test | Badge |
|-----|--------|
|__Python3.6__| [![Python3.6 Test Status]({BADGE_TEST_PY36_LINK})]({WORKFLOW_TEST_PY36_LINK})     |
|__Python3.7__| [![Python3.7 Test Status]({BADGE_TEST_PY37_LINK})]({WORKFLOW_TEST_PY37_LINK})     |
|__Python3.8__| [![Python3.8 Test Status]({BADGE_TEST_PY38_LINK})]({WORKFLOW_TEST_PY38_LINK})     |
|__Python3.9__| [![Python3.9 Test Status]({BADGE_TEST_PY39_LINK})]({WORKFLOW_TEST_PY39_LINK})     |
|__Python3.10__| [![Python3.10 Test Status]({BADGE_TEST_PY310_LINK})]({WORKFLOW_TEST_PY310_LINK}) |


| Security | Badge |
|-----|--------|
|__OSCS__| [![OSCS Status](https://www.oscs1024.com/platform/badge/albertmenglongli/pythonic-toolbox.svg?size=small)](https://www.oscs1024.com/project/albertmenglongli/pythonic-toolbox?ref=badge_small)   |


## Installation

```bash
pip3 install pythonic-toolbox --upgrade
```""")

DIR_PATH = Path(__file__).resolve().parent
README_PATH = DIR_PATH.parent / 'README.md'


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


def main():
    test_file_paths: List[Path] = get_testing_file_paths_under_current_module()
    contents: List[str] = [TITLE, '## Usage']
    title_level = 3
    for testing_file_path in sorted(test_file_paths, key=lambda x: x.name):
        pkg_name = testing_file_path.stem
        pkg_name_without_test_ = remove_prefix(pkg_name, 'test_')
        contents.append(SHARP * title_level + SPACE + pkg_name_without_test_)
        pkg = __import__(pkg_name)
        name_func_pairs = get_functions_in_pkg(pkg)
        for func_name, func in sorted(name_func_pairs, key=itemgetter(0)):
            title_level += 1
            func_name_without_test_ = remove_prefix(func_name, 'test_')
            contents.append(SHARP * title_level + SPACE + func_name_without_test_)

            source_code_str = getsource(func)
            source_codes_lines = deque(source_code_str.split('\n'))
            source_codes_lines.popleft()  # remove first line for def function
            source_codes_lines.appendleft(THREE_BACKTICKS + 'python3')
            source_codes_lines.append(THREE_BACKTICKS)
            # de-indent the codes
            source_codes_lines = [remove_prefix(line, SPACE * 4) for line in source_codes_lines]
            reformatted_source_code_str = '\n'.join(source_codes_lines)
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


if __name__ == '__main__':
    main()
