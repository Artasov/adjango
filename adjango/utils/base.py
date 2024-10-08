import asyncio
import functools
import json
import logging
import time
from pprint import pprint
from time import time

import aiohttp
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.handlers.asgi import ASGIRequest
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.http import HttpResponseNotAllowed, HttpResponse, QueryDict, RawPostDataException
from django.shortcuts import redirect

from adjango.utils.common import traceback_str
from adjango.utils.mail import send_emails


async def download_file_to_temp(url: str) -> ContentFile:
    """
    Скачивает файл с URL и сохраняет его в объект ContentFile, не сохраняя на диск.

    @param url: URL файла, который нужно скачать.
    @return: Временный файл в памяти.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                file_content = await response.read()
                file_name = url.split('/')[-1]
                return ContentFile(file_content, name=file_name)
            raise ValueError(f"Failed to download image from {url}, status code: {response.status}")


def add_user_to_group(user, group_name):
    group, created = Group.objects.get_or_create(name=group_name)
    if user not in group.user_set.all():
        group.user_set.add(user)


def allowed_only(allowed_methods):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if request.method in allowed_methods:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseNotAllowed(allowed_methods)

        return wrapped_view

    return decorator


def aallowed_only(allowed_methods) -> callable:
    def decorator(view_func) -> callable:
        async def wrapped_view(request, *args, **kwargs) -> HttpResponse:
            if request.method in allowed_methods:
                if asyncio.iscoroutinefunction(view_func):
                    return await view_func(request, *args, **kwargs)
                else:
                    return view_func(request, *args, **kwargs)
            else:
                return HttpResponseNotAllowed(allowed_methods)

        return wrapped_view

    return decorator


async def apprint(*args, **kwargs):
    await sync_to_async(pprint)(*args, **kwargs)


def force_data(fn):
    @functools.wraps(fn)
    def _wrapped_view(request, *args, **kwargs):
        data = {}

        if isinstance(request.POST, QueryDict):  # Объединяем данные из request.POST
            data.update(request.POST.dict())
        else:
            data.update(request.POST)

        if isinstance(request.GET, QueryDict):  # Объединяем данные из request.GET
            data.update(request.GET.dict())
        else:
            data.update(request.GET)

        try:  # Обрабатываем JSON-тело запроса, если оно есть
            json_data = json.loads(request.body)
            if isinstance(json_data, dict):
                data.update(json_data)
        except (ValueError, TypeError, RawPostDataException):
            pass

        setattr(request, 'get_data', lambda: data)
        return fn(request, *args, **kwargs)

    return _wrapped_view


def aforce_data(fn):
    @functools.wraps(fn)
    async def _wrapped_view(request, *args, **kwargs):
        if isinstance(request.POST, QueryDict):  # Объединяем данные из request.POST
            request.data.update(request.POST.dict())
        else:
            request.data.update(request.POST)

        if isinstance(request.GET, QueryDict):  # Объединяем данные из request.GET
            request.data.update(request.GET.dict())
        else:
            request.data.update(request.GET)

        try:  # Обрабатываем JSON-тело запроса, если оно есть
            json_data = json.loads(request.body.decode('utf-8'))
            if isinstance(json_data, dict):
                request.data.update(json_data)
        except (ValueError, TypeError, UnicodeDecodeError, RawPostDataException):
            pass

        return await fn(request, *args, **kwargs)

    return _wrapped_view


def acontroller(name=None, logger=settings.ADJANGO_LOGGER_NAME, log_name=True, log_time=False) -> callable:
    def decorator(fn) -> callable:
        @functools.wraps(fn)
        async def inner(request: ASGIRequest, *args, **kwargs):
            log = logging.getLogger(logger)
            fn_name = name or fn.__name__
            if log_name: log.info(f'ACtrl: {request.method} | {fn_name}')
            if log_time:
                start_time = time()

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


def controller(name=None, logger=settings.ADJANGO_LOGGER_NAME, log_name=True, log_time=False,
               auth_required=False, not_auth_redirect=settings.LOGIN_URL) -> callable:
    def decorator(fn) -> callable:
        @functools.wraps(fn)
        def inner(request: WSGIRequest, *args, **kwargs):
            log = logging.getLogger(logger)
            fn_name = name or fn.__name__
            if log_name: log.info(f'Ctrl: {request.method} | {fn_name}')
            if log_time: start_time = time()
            if auth_required:
                if not request.user.is_authenticated: return redirect(not_auth_redirect)
            if settings.DEBUG:
                with transaction.atomic():
                    return fn(request, *args, **kwargs)
            else:
                try:
                    if log_time:
                        end_time = time()
                        elapsed_time = end_time - start_time
                        log.info(f"Execution time of {fn_name}: {elapsed_time:.2f} seconds")
                    with transaction.atomic():
                        return fn(request, *args, **kwargs)
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
