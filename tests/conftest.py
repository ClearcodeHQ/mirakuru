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

IS_TRAVIS = 'TRAVIS' in os.environ
IS_PYPY_35 = platform.python_implementation() == 'PyPy' and sys.version_info < (3, 6)


simplefilter(
    'default',
    ResourceWarning
)


@pytest.fixture(autouse=True)
def error_warn(recwarn):
    """Raise error whenever any warning gets listed."""
    yield
    if recwarn.list and not (IS_PYPY_35 and IS_TRAVIS):
        raise recwarn.list[0].message
