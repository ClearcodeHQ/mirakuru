"""Small retry callable in case of specific error occurred."""

from datetime import datetime, timedelta, timezone
from time import sleep
from typing import TypeVar, Callable, Type

from mirakuru import ExecutorError


T = TypeVar("T")


def retry(
    func: Callable[[], T],
    timeout: int = 60,
    possible_exception: Type[Exception] = ExecutorError,
) -> T:
    """Attempt to retry the function for timeout time."""
    time: datetime = datetime.now(timezone.utc)
    timeout_diff: timedelta = timedelta(seconds=timeout)
    i = 0
    while True:
        i += 1
        try:
            res = func()
            return res
        except possible_exception as e:
            if time + timeout_diff < datetime.now(timezone.utc):
                raise TimeoutError(
                    "Failed after {i} attempts".format(i=i)
                ) from e
            sleep(1)
