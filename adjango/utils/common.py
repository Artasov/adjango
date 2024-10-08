import traceback


def traceback_str(error: BaseException) -> str:
    return ''.join(traceback.format_exception(type(error), error, error.__traceback__))
