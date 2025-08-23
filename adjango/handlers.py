# handlers.py
from __future__ import annotations

from abc import ABC, abstractmethod

from django.core.handlers.asgi import ASGIRequest
from django.core.handlers.wsgi import WSGIRequest

from adjango.utils.celery.tasker import Tasker
from adjango.utils.common import traceback_str


class IHandlerControllerException(ABC):
    @staticmethod
    @abstractmethod
    def handle(fn_name: str, request: WSGIRequest | ASGIRequest, e: Exception, *args, **kwargs) -> None:
        """
        Example exception handling function.

        :param fn_name: Name of function where exception occurred.
        :param request: Request object (WSGIRequest or ASGIRequest).
        :param e: Exception to handle.
        :param args: Positional arguments passed to function.
        :param kwargs: Named arguments passed to function.

        :return: None

        @usage:
            _handling_function(fn_name, request, e)
        """
        pass


class HCE(IHandlerControllerException):
    """
    Example implementation of controller exception handler.
    """

    @staticmethod
    def handle(fn_name: str, request: WSGIRequest | ASGIRequest, e: Exception, *args, **kwargs) -> None:
        """
        Example exception handling function.

        :param fn_name: Name of function where exception occurred.
        :param request: Request object (WSGIRequest or ASGIRequest).
        :param e: Exception to handle.
        :param args: Positional arguments passed to function.
        :param kwargs: Named arguments passed to function.

        :return: None

        @usage:
            _handling_function(fn_name, request, e)
        """
        import logging

        from django.conf import settings

        from adjango.tasks import send_emails_task

        log = logging.getLogger('global')
        error_text = (
            f'ERROR in {fn_name}:\n'
            f'{traceback_str(e)}\n'
            f'{request.POST=}\n'
            f'{request.GET=}\n'
            f'{request.FILES=}\n'
            f'{request.COOKIES=}\n'
            f'{request.user=}\n'
            f'{args=}\n'
            f'{kwargs=}'
        )
        log.error(error_text)
        if not settings.DEBUG:
            Tasker.put(
                send_emails_task,
                subject='SERVER ERROR',
                emails=(
                    'admin@example.com',
                    'admin2@example.com',
                ),
                template='admin/exception_report.html',
                context={'error': error_text},
            )
