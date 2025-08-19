# test_decorators.py
import json
import logging
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, QueryDict
from django.test import RequestFactory

from adjango.decorators import admin_label, controller, force_data, task


class TestAdminLabel:
    """Tests for декоратора admin_label"""

    def test_admin_label_decorator(self):
        """Test установки label для функции"""

        @admin_label("Custom Label")
        def test_function():
            pass

        assert hasattr(test_function, "label")
        assert test_function.label == "Custom Label"


class TestTask:
    """Tests for декоратора task"""

    @patch("adjango.decorators.logging.getLogger")
    def test_task_with_logger(self, mock_get_logger):
        """Test task декоратора с логированием"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        @task(logger="test_logger")
        def test_task(arg1, arg2, kwarg1=None):
            return "result"

        result = test_task("value1", "value2", kwarg1="kwvalue1")

        assert result == "result"
        mock_get_logger.assert_called_with("test_logger")
        assert mock_logger.info.call_count == 2  # start and end
        mock_logger.info.assert_any_call(
            "Start executing task: test_task\n('value1', 'value2')\n{'kwarg1': 'kwvalue1'}"
        )
        mock_logger.info.assert_any_call(
            "End executing task: test_task\n('value1', 'value2')\n{'kwarg1': 'kwvalue1'}"
        )

    @patch("adjango.decorators.logging.getLogger")
    @patch("adjango.decorators.traceback_str")
    def test_task_with_exception(self, mock_traceback_str, mock_get_logger):
        """Test обработки исключений в task"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_traceback_str.return_value = "Test traceback"

        @task(logger="test_logger")
        def failing_task():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_task()

        mock_logger.critical.assert_any_call("Error executing task: failing_task")
        mock_logger.critical.assert_any_call("Test traceback")

    def test_task_without_logger(self):
        """Test task декоратора без логирования"""

        @task()
        def test_task():
            return "result"

        result = test_task()
        assert result == "result"


class TestForceData:
    """Tests for декоратора force_data"""

    def test_force_data_basic(self):
        """Test базовой функциональности force_data"""

        @force_data
        def mock_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=WSGIRequest)
        request.POST = QueryDict("post_key=post_value")
        request.GET = QueryDict("get_key=get_value")
        request.body = b'{"json_key": "json_value"}'

        response = mock_view(request)

        assert response.status_code == 200
        assert hasattr(request, "data")
        assert request.data["post_key"] == "post_value"
        assert request.data["get_key"] == "get_value"
        assert request.data["json_key"] == "json_value"

    def test_force_data_invalid_json(self):
        """Test обработки невалидного JSON"""

        @force_data
        def mock_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=WSGIRequest)
        request.POST = QueryDict("post_key=post_value")
        request.GET = QueryDict("get_key=get_value")
        request.body = b"invalid json"

        response = mock_view(request)

        assert response.status_code == 200
        assert hasattr(request, "data")
        assert "json_key" not in request.data
        assert request.data["post_key"] == "post_value"

    def test_force_data_existing_data(self):
        """Test с уже существующим атрибутом data"""

        @force_data
        def mock_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=WSGIRequest)
        request.data = {"existing": "value"}
        request.POST = QueryDict("post_key=post_value")
        request.GET = QueryDict("get_key=get_value")
        request.body = b'{"json_key": "json_value"}'

        response = mock_view(request)

        assert response.status_code == 200
        assert request.data["existing"] == "value"
        assert request.data["post_key"] == "post_value"


class TestController:
    """Tests for декоратора controller"""

    @patch("adjango.decorators.logging.getLogger")
    def test_controller_basic(self, mock_get_logger):
        """Test базовой функциональности controller"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        @controller()
        def mock_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=WSGIRequest)
        request.method = "GET"
        request.user = MagicMock()
        request.user.is_authenticated = True

        with patch.object(settings, "DEBUG", True):
            response = mock_view(request)

        assert response.status_code == 200

    @patch("adjango.decorators.logging.getLogger")
    def test_controller_with_logging(self, mock_get_logger):
        """Test логирования в controller"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        @controller(name="test_controller", log_name=True, log_time=True)
        def mock_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=WSGIRequest)
        request.method = "POST"
        request.user = MagicMock()
        request.user.is_authenticated = True

        with patch.object(settings, "DEBUG", True):
            response = mock_view(request)

        assert response.status_code == 200
        mock_logger.info.assert_called()

    @patch("adjango.decorators.redirect")
    def test_controller_auth_required_not_authenticated(self, mock_redirect):
        """Test редиректа при отсутствии аутентификации"""
        mock_redirect.return_value = HttpResponse(status=302)

        @controller(auth_required=True)
        def mock_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=WSGIRequest)
        request.method = "GET"
        request.user = MagicMock()
        request.user.is_authenticated = False

        response = mock_view(request)

        assert response.status_code == 302
        mock_redirect.assert_called_once()

    @patch("adjango.decorators.logging.getLogger")
    @patch("adjango.decorators.traceback_str")
    def test_controller_exception_handling(self, mock_traceback_str, mock_get_logger):
        """Test обработки исключений в controller"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_traceback_str.return_value = "Test traceback"

        @controller()
        def mock_view(request):
            raise ValueError("Test error")

        request = MagicMock(spec=WSGIRequest)
        request.method = "GET"
        request.user = MagicMock()
        request.user.is_authenticated = True

        with patch.object(settings, "DEBUG", False):
            with pytest.raises(ValueError):
                mock_view(request)

        mock_logger.critical.assert_called()

    @patch("adjango.decorators.logging.getLogger")
    def test_controller_exception_handling_function(self, mock_get_logger):
        """Test кастомной функции обработки исключений"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        mock_handling_function = MagicMock()

        @controller()
        def mock_view(request):
            raise ValueError("Test error")

        request = MagicMock(spec=WSGIRequest)
        request.method = "GET"
        request.user = MagicMock()
        request.user.is_authenticated = True

        with patch.object(settings, "DEBUG", False):
            with patch(
                "adjango.decorators.ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION",
                mock_handling_function,
            ):
                with pytest.raises(ValueError):
                    mock_view(request)

        mock_handling_function.assert_called_once()

    def test_controller_auth_required_authenticated(self):
        """Test успешного прохождения аутентификации"""

        @controller(auth_required=True)
        def mock_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=WSGIRequest)
        request.method = "GET"
        request.user = MagicMock()
        request.user.is_authenticated = True

        with patch.object(settings, "DEBUG", True):
            response = mock_view(request)

        assert response.status_code == 200
