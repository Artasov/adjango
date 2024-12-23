# decorators.py
from __future__ import annotations

import json
import logging
from functools import wraps
from time import time
from typing import Callable, Any

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseNotAllowed, HttpResponse, QueryDict, RawPostDataException
from django.shortcuts import redirect

from adjango.conf import ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION, ADJANGO_CONTROLLERS_LOGGING, \
    ADJANGO_CONTROLLERS_LOGGER_NAME
from adjango.utils.common import traceback_str


def admin_description(description: str):
    def decorator(func):
        func.short_description = description
        return func

    return decorator


def admin_order_field(field: str):
    def decorator(func):
        func.admin_order_field = field
        return func

    return decorator


def admin_allow_tags(allow: bool = True):
    def decorator(func):
        func.allow_tags = allow
        return func

    return decorator


def task(logger: str = None):
    """
    Декоратор для задач Celery, который логирует начало и конец выполнения задачи и её ошибки.

    :param logger: Имя логгера для логирования. Если не передано, логирование не будет выполнено.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = None
            if logger:
                log = logging.getLogger(logger)
                log.info(f"Start executing task: {func.__name__}\n{args}\n{kwargs}")
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                log.critical(f'Error executing task: {func.__name__}')
                log.critical(traceback_str(e))
                raise e
            if log: log.info(f"End executing task: {func.__name__}\n{args}\n{kwargs}")
            return result

        return wrapper

    return decorator


def allowed_only(allowed_methods: list[str]) -> Callable[[Callable[..., HttpResponse]], Callable[..., HttpResponse]]:
    """
    Декоратор для ограничения методов запроса.

    :param allowed_methods: Список разрешенных методов (GET, POST и т.д.).

    :return: Функция, которая ограничивает вызов view-функции в зависимости от метода запроса.

    @usage:
        @allowed_only(['GET', 'POST'])
        def my_view(request):
            ...
    """

    def decorator(fn: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        def wrapped_view(request: WSGIRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            if request.method in allowed_methods:
                return fn(request, *args, **kwargs)
            else:
                return HttpResponseNotAllowed(allowed_methods)

        return wrapped_view

    return decorator


def force_data(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Декоратор для объединения данных из POST, GET и JSON тела запроса.

    :param fn: Функция, которая будет обернута.

    :return: Функция, в которой объединены данные из разных частей запроса.

    @usage:
        @force_data
        def my_view(request):
            print(request.data)
    """

    @wraps(fn)
    def _wrapped_view(request: WSGIRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not hasattr(request, 'data'): request.data = {}
        request.data.update(request.POST.dict() if isinstance(request.POST, QueryDict) else request.POST)
        request.data.update(request.GET.dict() if isinstance(request.GET, QueryDict) else request.GET)
        try:
            json_data = json.loads(request.body.decode('utf-8'))
            if isinstance(json_data, dict): request.data.update(json_data)
        except (ValueError, TypeError, UnicodeDecodeError, RawPostDataException):
            pass
        return fn(request, *args, **kwargs)

    return _wrapped_view


def controller(
        name: str | None = None,
        logger: str = None,
        log_name: bool = True,
        log_time: bool = False,
        auth_required: bool = False,
        not_auth_redirect: str = settings.LOGIN_URL
) -> Callable[..., Any]:
    """
    Синхронный контроллер с логированием, проверкой аутентификации и обработкой исключений.

    :param name: Название контроллера.
    :param logger: Имя логгера для записи сообщений.
    :param log_name: Логировать имя контроллера.
    :param log_time: Логировать время выполнения контроллера.
    :param auth_required: Проверять ли аутентификацию пользователя.
    :param not_auth_redirect: URL для редиректа, если пользователь не аутентифицирован.

    :return: Синхронный контроллер с логированием и обработкой исключений.

    @usage:
        @controller
        def my_view(request):
            ...
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def inner(request: WSGIRequest, *args: Any, **kwargs: Any) -> Any:
            log = logging.getLogger(logger or ADJANGO_CONTROLLERS_LOGGER_NAME)
            fn_name = name or fn.__name__
            start_time = None
            if log_name or (log_name is None and ADJANGO_CONTROLLERS_LOGGING):
                log.info(f'Ctrl: {request.method} | {fn_name}')
            if log_time: start_time = time()
            if auth_required and not request.user.is_authenticated: return redirect(not_auth_redirect)
            if settings.DEBUG:
                result = fn(request, *args, **kwargs)
                if log_time:
                    end_time = time()
                    elapsed_time = end_time - start_time
                    log.info(f"Execution time {fn_name}: {elapsed_time:.2f} seconds")
                return result
            else:
                try:
                    result = fn(request, *args, **kwargs)
                    if log_time:
                        end_time = time()
                        elapsed_time = end_time - start_time
                        log.info(f"Execution time {fn_name}: {elapsed_time:.2f} seconds")
                    return result
                except Exception as e:
                    log.critical(f"ERROR in {fn_name}: {traceback_str(e)}", exc_info=True)
                    if hasattr(settings, 'ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION'):
                        handling_function = ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION
                        if callable(handling_function): handling_function(fn_name, request, e, *args, **kwargs)
                    raise e

        return inner

    return decorator
