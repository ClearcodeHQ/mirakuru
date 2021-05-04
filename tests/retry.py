"""Small retry callable in case of specific error occured"""

from datetime import datetime, timedelta
from time import sleep

from mirakuru import ExecutorError


def retry(func, timeout: int = 60, possible_exception=ExecutorError):
    """
    Attempt to retry the function for timeout time.
    """
    time: datetime = datetime.utcnow()
    timeout_diff: timedelta = timedelta(seconds=timeout)
    i = 0
    while True:
        i += 1
        try:
            res = func()
            return res
        except possible_exception as e:
            if time + timeout_diff < datetime.utcnow():
                raise TimeoutError("Faile after {i} attempts".format(i=i)) \
                    from e
            sleep(1)
            pass
