import re
import sys
from pathlib import Path

from setuptools import setup, find_packages

# handle version info from version.py in project
__version__ = None
filepath = 'pythonic_toolbox/version.py'
with open(filepath, 'r') as version_file:
    try:
        content = version_file.read()
        version_match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", content, re.M)

    except Exception as error:
        print(f'Failed to find version info`: {error}')
        sys.exit(1)
    else:
        if version_match:
            __version__ = version_match.group(1)

if not __version__:
    raise RuntimeError('version is not set successfully')

# read the contents of your README file
long_description = (Path(__file__).parent / "README.md").read_text()

url = 'https://github.com/albertmenglongli/pythonic-toolbox'

setup(
    name='pythonic-toolbox',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=__version__,

    description='a toolbox with pythonic utils, tools',
    long_description=long_description,
    long_description_content_type='text/markdown',

    # The project's main homepage.
    url='https://github.com/albertmenglongli/pythonic-toolbox',

    # Author details
    author='menglong.li',
    author_email='albert.menglongli@gmail.com',

    # Choose your license
    license='Apache2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    # What does your project relate to?
    keywords=['toolbox'],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    py_modules=["pythonic_toolbox"],

    install_requires=[
        "setuptools",
        "funcy>=1.16",
    ],
    extras_require={
        "test": [
            "pytest",
            "wheel",
        ]
    }

)
