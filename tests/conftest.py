"""
Conftest responsible for filtering ResourceWarning for python 3.

Also includes fixture for raising an error whenever we leave any resource open.
"""
import sys
from warnings import simplefilter

import pytest


if sys.version_info[0] == '3':
    from exceptions import ResourceWarning
    simplefilter('default', ResourceWarning)


@pytest.fixture(autouse=True)
def error_warn(request, recwarn):
    """Raise error whenever any warning gets listed."""
    def list_errors_and_error():
        if recwarn.list:
            raise recwarn.list[0].message

    request.addfinalizer(list_errors_and_error)
