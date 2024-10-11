from __future__ import annotations

import asyncio
import json
import logging
from functools import wraps
from time import time
from typing import Callable, Any

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponseNotAllowed, HttpResponse, QueryDict, RawPostDataException

from adjango.utils.base import AsyncAtomicContextManager
from adjango.utils.common import traceback_str
from adjango.utils.funcs import auser_passes_test
from adjango.utils.mail import send_emails


def aforce_data(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Асинхронный декоратор для объединения данных из POST, GET и JSON тела запроса.

    @param fn: Асинхронная функция, которая будет обернута.

    @return: Асинхронная функция, в которой объединены данные из разных частей запроса.

    @usage:
        @force_data
        def my_view(request):
            print(request.data)
    """

    @wraps(fn)
    async def _wrapped_view(request: ASGIRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not hasattr(request, 'data'): request.data = {}
        request.data.update(request.POST.dict() if isinstance(request.POST, QueryDict) else request.POST)
        request.data.update(request.GET.dict() if isinstance(request.GET, QueryDict) else request.GET)
        try:
            json_data = json.loads(request.body.decode('utf-8'))
            if isinstance(json_data, dict): request.data.update(json_data)
        except (ValueError, TypeError, UnicodeDecodeError, RawPostDataException):
            pass
        return await fn(request, *args, **kwargs)

    return _wrapped_view


def aatomic(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Асинхронный декоратор, который оборачивает представление в контекст менеджера транзакций.

    @usage: @aatomic
            async def my_view(request): ...
    """

    @wraps(fn)
    async def _wrapped_view(request: ASGIRequest, *args: Any, **kwargs: Any) -> Any:
        async with AsyncAtomicContextManager():
            return await fn(request, *args, **kwargs)

    return _wrapped_view


def acontroller(
        name: str | None = None,
        logger: str = None,
        log_name: bool = None,
        log_time: bool = False
) -> Callable[..., Any]:
    """
    Асинхронный контроллер с логированием и обработкой исключений.

    @param name: Название контроллера.
    @param logger: Имя логгера для записи сообщений.
    @param log_name: Логировать имя контроллера.
    @param log_time: Логировать время выполнения контроллера.

    @return: Асинхронный контроллер с логированием и обработкой исключений.

    @usage:
        @acontroller
        async def my_view(request):
            ...
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        async def inner(request: ASGIRequest, *args: Any, **kwargs: Any) -> Any:
            log = logging.getLogger(logger or settings.ADJANGO_CONTROLLERS_LOGGER_NAME)
            fn_name = name or fn.__name__
            start_time = None
            if log_name or (log_name is None and settings.ADJANGO_CONTROLLERS_LOGGING):
                log.info(f'ACtrl: {request.method} | {fn_name}')

            if log_time: start_time = time()
            if settings.DEBUG:
                return await fn(request, *args, **kwargs)
            else:
                try:
                    if log_time:
                        end_time = time()
                        elapsed_time = end_time - start_time
                        log.info(f"Execution time of {fn_name}: {elapsed_time:.2f} seconds")
                    return await fn(request, *args, **kwargs)
                except Exception as e:
                    log.critical(f"ERROR in {fn_name}: {traceback_str(e)}", exc_info=True)
                    email_context = {
                        'subject': 'SERVER ERROR',
                        'emails': settings.ADJANGO_EXCEPTION_REPORT_EMAILS,
                        'template': settings.ADJANGO_EXCEPTION_REPORT_TEMPLATE,
                        'context': {'traceback': traceback_str(e), }
                    }
                    if settings.ADJANGO_USE_CELERY_MAIL_REPORT:
                        settings.ADJANGO_CELERY_SEND_MAIL_TASK.delay(**email_context)
                    else:
                        send_emails(**email_context)
                    raise e

        return inner

    return decorator


def aallowed_only(allowed_methods: list[str]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Асинхронный декоратор для ограничения методов запроса.

    @param allowed_methods: Список разрешенных методов (GET, POST и т.д.).

    @return: Асинхронная функция, которая ограничивает вызов view-функции в зависимости от метода запроса.

    @usage:
        @aallowed_only(['GET', 'POST'])
        async def my_view(request):
            ...
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapped_view(request: ASGIRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            if request.method in allowed_methods:
                if asyncio.iscoroutinefunction(fn):
                    return await fn(request, *args, **kwargs)
                else:
                    return fn(request, *args, **kwargs)
            else:
                return HttpResponseNotAllowed(allowed_methods)

        return wrapped_view

    return decorator


def alogin_required(
        function: Callable[..., Any] | None = None,
        redirect_field_name: str = REDIRECT_FIELD_NAME,
        login_url: str | None = None,
) -> Callable[..., Any]:
    """
    Asynchronous decorator for views that checks if the user is authenticated,
    redirecting to the login page if necessary.
    """
    actual_decorator = auser_passes_test(
        sync_to_async(lambda u: u.is_authenticated),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
