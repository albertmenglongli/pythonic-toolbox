from pathlib import Path
from typing import List
from collections import deque

from inspect import getmembers, isfunction, getsource

DIR_PATH = Path(__file__).resolve().parent
README_PATH = DIR_PATH.parent.parent / 'README.md'

SPACE = ' '
THREE_BACKTICKS = '```'
NEW_LINE = '\n'
SHARP = '#'


def get_testing_file_paths_under_current_module() -> List[Path]:
    global DIR_PATH
    file_paths = [x for x in DIR_PATH.iterdir() if not x.is_dir()]
    testing_file_paths = [x for x in file_paths if x.name.startswith('test_')]
    return testing_file_paths


def get_functions_in_pkg(pkg):
    return getmembers(pkg, isfunction)


title = ("""# Pythonic toolbox

This **README.md** is **Auto-Generated** from testing files by **generate_readme_markdown.py** .
 
**DO NOT EDIT DIRECTLY!**

## Installation

A python toolbox with multi useful utils, functions, decorators in pythonic way.

```bash
pip install pythonic-toolbox 
```""")


def get_title():
    global title
    return title


# remove_prefix is introduced after Python 3.9
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


if __name__ == '__main__':
    test_file_paths: List[Path] = get_testing_file_paths_under_current_module()
    contents: List[str] = [get_title(), '# How to use']

    title_level = 3

    for testing_file_path in sorted(test_file_paths, key=lambda x: x.name):
        pkg_name = testing_file_path.stem
        pkg_name_without_test_ = remove_prefix(pkg_name, 'test_')
        contents.append(SHARP * title_level + SPACE + pkg_name_without_test_)
        pkg = __import__(pkg_name)
        name_func_pairs = get_functions_in_pkg(pkg)
        for func_name, func in sorted(name_func_pairs, key=lambda item: item[0]):
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
