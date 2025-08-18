# test_handlers.py
from unittest.mock import MagicMock, patch

import pytest
from django.core.handlers.asgi import ASGIRequest
from django.core.handlers.wsgi import WSGIRequest

from adjango.handlers import HCE, IHandlerControllerException


class TestIHandlerControllerException:
    """Тесты для интерфейса IHandlerControllerException"""

    def test_interface_abstract_method(self):
        """Тест что интерфейс является абстрактным"""

        with pytest.raises(TypeError):
            # Не должен позволять создавать экземпляр напрямую
            IHandlerControllerException()

    def test_interface_must_implement_handle(self):
        """Тест что наследники должны реализовать handle"""

        class IncompleteHandler(IHandlerControllerException):
            pass

        with pytest.raises(TypeError):
            # Должен требовать реализации абстрактного метода
            IncompleteHandler()

    def test_interface_with_implementation(self):
        """Тест корректной реализации интерфейса"""

        class CompleteHandler(IHandlerControllerException):
            @staticmethod
            def handle(fn_name, request, e, *args, **kwargs):
                return "handled"

        # Должен позволить создать экземпляр
        handler = CompleteHandler()
        assert handler is not None
        assert handler.handle("test", None, Exception()) == "handled"


class TestHCE:
    """Тесты для HCE (Handler Controller Exception)"""

    @patch("logging.getLogger")
    @patch("adjango.handlers.Tasker.put")
    @patch("adjango.tasks.send_emails_task")
    @patch("adjango.handlers.traceback_str")
    def test_hce_handle_with_debug_false(
        self, mock_traceback_str, mock_send_emails_task, mock_tasker_put, mock_get_logger
    ):
        """Тест обработки исключения в production режиме"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_traceback_str.return_value = "Test traceback"

        request = MagicMock(spec=WSGIRequest)
        request.POST = {"key": "value"}
        request.GET = {"param": "test"}
        request.FILES = {}
        request.COOKIES = {"session": "abc123"}
        request.user = "test_user"

        exception = ValueError("Test error")

        with patch("django.conf.settings.DEBUG", False):
            HCE.handle("test_function", request, exception, "arg1", kwarg1="value1")

        # Проверяем что было залогировано
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert "test_function" in error_call_args
        assert "Test traceback" in error_call_args
        assert "request.POST" in error_call_args
        assert "request.GET" in error_call_args

        # Проверяем что была поставлена задача отправки email
        mock_tasker_put.assert_called_once()
        call_args = mock_tasker_put.call_args
        assert call_args[0][0] == mock_send_emails_task
        assert call_args[1]["subject"] == "SERVER ERROR"
        assert "admin@example.com" in call_args[1]["emails"]
        assert "admin2@example.com" in call_args[1]["emails"]
        assert call_args[1]["template"] == "admin/exception_report.html"

    @patch("logging.getLogger")
    @patch("adjango.handlers.Tasker.put")
    @patch("adjango.handlers.traceback_str")
    def test_hce_handle_with_debug_true(self, mock_traceback_str, mock_tasker_put, mock_get_logger):
        """Тест обработки исключения в debug режиме"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_traceback_str.return_value = "Test traceback"

        request = MagicMock(spec=ASGIRequest)
        request.POST = {}
        request.GET = {}
        request.FILES = {}
        request.COOKIES = {}
        request.user = "test_user"

        exception = RuntimeError("Test runtime error")

        with patch("django.conf.settings.DEBUG", True):
            HCE.handle("test_function", request, exception)

        # Проверяем что было залогировано
        mock_logger.error.assert_called_once()

        # Проверяем что НЕ была поставлена задача отправки email в debug режиме
        mock_tasker_put.assert_not_called()

    @patch("logging.getLogger")
    @patch("adjango.handlers.traceback_str")
    def test_hce_handle_with_asgi_request(self, mock_traceback_str, mock_get_logger):
        """Тест обработки с ASGI запросом"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_traceback_str.return_value = "ASGI traceback"

        request = MagicMock(spec=ASGIRequest)
        request.POST = {"asgi_key": "asgi_value"}
        request.GET = {}
        request.FILES = {}
        request.COOKIES = {}
        request.user = "asgi_user"

        exception = Exception("ASGI error")

        with patch("django.conf.settings.DEBUG", True):
            HCE.handle("asgi_function", request, exception, "asgi_arg")

        # Проверяем что лог содержит информацию об ASGI запросе
        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "asgi_function" in error_message
        assert "ASGI traceback" in error_message
        assert "asgi_key" in error_message

    @patch("logging.getLogger")
    @patch("adjango.handlers.traceback_str")
    def test_hce_handle_with_args_kwargs(self, mock_traceback_str, mock_get_logger):
        """Тест обработки с дополнительными аргументами"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_traceback_str.return_value = "Args test traceback"

        request = MagicMock(spec=WSGIRequest)
        request.POST = {}
        request.GET = {}
        request.FILES = {}
        request.COOKIES = {}
        request.user = "test_user"

        exception = Exception("Args test error")

        with patch("django.conf.settings.DEBUG", True):
            HCE.handle("args_function", request, exception, "arg1", "arg2", kwarg1="value1", kwarg2="value2")

        # Проверяем что аргументы попали в лог
        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "args=('arg1', 'arg2')" in error_message
        assert "kwargs={'kwarg1': 'value1', 'kwarg2': 'value2'}" in error_message

    def test_hce_implements_interface(self):
        """Тест что HCE корректно реализует интерфейс"""

        # Проверяем что HCE наследует от IHandlerControllerException
        assert issubclass(HCE, IHandlerControllerException)

        # Проверяем что можно создать экземпляр
        handler = HCE()
        assert handler is not None

        # Проверяем что метод handle статический
        assert callable(HCE.handle)

    @patch("logging.getLogger")
    @patch("adjango.handlers.traceback_str")
    def test_hce_handle_logger_name(self, mock_traceback_str, mock_get_logger):
        """Тест использования правильного логгера"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_traceback_str.return_value = "Logger test traceback"

        request = MagicMock(spec=WSGIRequest)
        request.POST = {}
        request.GET = {}
        request.FILES = {}
        request.COOKIES = {}
        request.user = "test_user"

        exception = Exception("Logger test error")

        with patch("django.conf.settings.DEBUG", True):
            HCE.handle("logger_function", request, exception)

        # Проверяем что использовался логгер "global"
        mock_get_logger.assert_called_with("global")

    @patch("logging.getLogger")
    @patch("adjango.handlers.Tasker.put")
    @patch("adjango.handlers.traceback_str")
    def test_hce_handle_email_context(self, mock_traceback_str, mock_tasker_put, mock_get_logger):
        """Тест контекста для email уведомления"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        expected_error_text = "Expected error text"
        mock_traceback_str.return_value = "Email test traceback"

        request = MagicMock(spec=WSGIRequest)
        request.POST = {"email_key": "email_value"}
        request.GET = {}
        request.FILES = {}
        request.COOKIES = {}
        request.user = "email_user"

        exception = Exception("Email test error")

        with patch("django.conf.settings.DEBUG", False):
            HCE.handle("email_function", request, exception)

        # Проверяем контекст email
        mock_tasker_put.assert_called_once()
        call_kwargs = mock_tasker_put.call_args[1]
        assert "context" in call_kwargs
        assert "error" in call_kwargs["context"]
