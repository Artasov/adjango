import os
import sys
import traceback


def is_celery() -> bool:
    """
    Проверяет, выполняется ли процесс в контексте Celery.

    @return: True, если Celery запущена, иначе False.

    @behavior:
        - Проверяет, содержит ли первый аргумент sys.argv слово 'celery', что указывает на запуск Celery.
        - Также проверяет наличие переменной окружения IS_CELERY, которая может быть установлена для обозначения того,
          что процесс является частью Celery.

    @usage:
        if is_celery():
            # Логика для выполнения внутри процесса Celery
    """
    return 'celery' in sys.argv[0] or os.getenv('IS_CELERY', False)


def traceback_str(error: BaseException) -> str:
    """
    Преобразует объект исключения в строковое представление полного стека вызовов.

    @param error: Объект исключения.

    @return: Строка с полным стеком вызовов, относящихся к исключению.

    @usage:
        try:
            ...
        except Exception as e:
            log.error(traceback_str(e))
    """
    return ''.join(traceback.format_exception(type(error), error, error.__traceback__))
