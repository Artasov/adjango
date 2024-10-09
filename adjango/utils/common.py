import os
import sys
import traceback


def is_celery():
    return 'celery' in sys.argv[0] or os.getenv('IS_CELERY', False)


def traceback_str(error: BaseException) -> str:
    return ''.join(traceback.format_exception(type(error), error, error.__traceback__))
