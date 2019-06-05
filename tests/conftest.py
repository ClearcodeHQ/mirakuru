"""
Tests pre-configuration.

* Filtering ResourceWarning for the Python 3.
* Fixture for raising an error whenever we leave any resource open.
"""
import platform
import os
import sys
from warnings import simplefilter

import pytest

is_travis = 'TRAVIS' in os.environ
is_pypy_35 = platform.python_implementation() == 'PyPy' and sys.version_info < (3, 6)


simplefilter(
    'default',
    ResourceWarning
)


@pytest.fixture(autouse=True)
def error_warn(recwarn):
    """Raise error whenever any warning gets listed."""
    yield
    if recwarn.list and not (is_pypy_35 and is_travis):
        raise recwarn.list[0].message
