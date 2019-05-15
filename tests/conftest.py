"""
Tests pre-configuration.

* Filtering ResourceWarning for the Python 3.
* Fixture for raising an error whenever we leave any resource open.
"""

from warnings import simplefilter

import pytest


simplefilter(
    'default',
    ResourceWarning
)


@pytest.fixture(autouse=True)
def error_warn(recwarn):
    """Raise error whenever any warning gets listed."""
    yield
    if recwarn.list:
        raise recwarn.list[0].message
