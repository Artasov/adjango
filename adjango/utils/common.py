# utils/common.py
import os
import sys
import traceback


def is_celery() -> bool:
    """
    Checks if process is running in Celery context.

    :return: True if Celery is running, otherwise False.

    @behavior:
        - Checks if first sys.argv argument contains 'celery', indicating Celery startup.
        - Also checks for IS_CELERY environment variable which can be set to indicate
          that process is part of Celery.

    @usage:
        if is_celery():
            # Logic for execution inside Celery process
    """
    return "celery" in sys.argv[0] or os.getenv("IS_CELERY", False)


def traceback_str(error: BaseException) -> str:
    """
    Converts exception object to string representation of full call stack.

    :param error: Exception object.

    :return: String with full call stack related to exception.

    @usage:
        try:
            ...
        except Exception as e:
            log.error(traceback_str(e))
    """
    return "".join(traceback.format_exception(type(error), error, error.__traceback__))
