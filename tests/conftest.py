"""
Tests pre-configuration.

* Filtering ResourceWarning for the Python 3.
* Fixture for raising an error whenever we leave any resource open.
"""

import sys
from warnings import simplefilter

import pytest


if sys.version_info >= (3,):
    from exceptions import ResourceWarning  # pylint: disable=no-name-in-module
    simplefilter('default', ResourceWarning)


@pytest.fixture(autouse=True)
def error_warn(recwarn):
    """Raise error whenever any warning gets listed."""
    yield
    if recwarn.list:
        raise recwarn.list[0].message
