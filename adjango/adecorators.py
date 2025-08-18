# adecorators.py
from __future__ import annotations

import asyncio
import json
import logging
from functools import wraps
from time import time
from typing import Any, Callable

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.handlers.asgi import ASGIRequest
from django.http import (
    HttpResponse,
    HttpResponseNotAllowed,
    QueryDict,
    RawPostDataException,
)

from adjango.conf import ADJANGO_CONTROLLERS_LOGGER_NAME, ADJANGO_CONTROLLERS_LOGGING
from adjango.utils.base import AsyncAtomicContextManager
from adjango.utils.common import traceback_str
from adjango.utils.funcs import auser_passes_test


def aforce_data(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Async decorator for merging data from POST, GET and JSON request body.

    :param fn: Async function to be wrapped.

    :return: Async function with merged data from different parts of request.

    @usage:
        @aforce_data
        async def my_view(request):
            print(request.data)
    """

    @wraps(fn)
    async def _wrapped_view(
        request: ASGIRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        if not hasattr(request, "data"):
            request.data = {}
        request.data.update(
            request.POST.dict() if isinstance(request.POST, QueryDict) else request.POST
        )
        request.data.update(
            request.GET.dict() if isinstance(request.GET, QueryDict) else request.GET
        )
        try:
            json_data = json.loads(request.body.decode("utf-8"))
            if isinstance(json_data, dict):
                request.data.update(json_data)
        except (ValueError, TypeError, UnicodeDecodeError, RawPostDataException):
            pass
        return await fn(request, *args, **kwargs)

    return _wrapped_view


def aatomic(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Async decorator that wraps view in transaction context manager.

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
    log_time: bool = False,
) -> Callable[..., Any]:
    """
    Async controller with logging and exception handling.

    :param name: Controller name.
    :param logger: Logger name for writing messages.
    :param log_name: Log controller name.
    :param log_time: Log controller execution time.

    :return: Async controller with logging and exception handling.

    @usage:
        @acontroller
        async def my_view(request):
            ...
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        async def inner(request: ASGIRequest, *args: Any, **kwargs: Any) -> Any:
            log = logging.getLogger(logger or ADJANGO_CONTROLLERS_LOGGER_NAME)
            fn_name = name or fn.__name__
            start_time = None
            if log_name or (log_name is None and ADJANGO_CONTROLLERS_LOGGING):
                log.info(f"ACtrl: {request.method} | {fn_name}")

            if log_time:
                start_time = time()
            if settings.DEBUG:
                result = await fn(request, *args, **kwargs)
                if log_time:
                    end_time = time()
                    elapsed_time = end_time - start_time
                    log.info(f"Execution time {fn_name}: {elapsed_time:.2f} seconds")
                return result
            else:
                try:
                    result = await fn(request, *args, **kwargs)
                    if log_time:
                        end_time = time()
                        elapsed_time = end_time - start_time
                        log.info(
                            f"Execution time {fn_name}: {elapsed_time:.2f} seconds"
                        )
                    return result
                except Exception as e:
                    log.critical(
                        f"ERROR in {fn_name}: {traceback_str(e)}", exc_info=True
                    )

                    raise e

        return inner

    return decorator


def aallowed_only(
    allowed_methods: list[str],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Async decorator for limiting request methods.

    :param allowed_methods: List of allowed methods (GET, POST etc.).

    :return: Async function that limits view function call depending on request method.

    @usage:
        @aallowed_only(['GET', 'POST'])
        async def my_view(request):
            ...
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapped_view(
            request: ASGIRequest, *args: Any, **kwargs: Any
        ) -> HttpResponse:
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
