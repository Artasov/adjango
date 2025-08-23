# test_adecorators.py
import asyncio
import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponse, HttpResponseNotAllowed, QueryDict
from django.test import RequestFactory

from adjango.adecorators import (
    aallowed_only,
    aatomic,
    acontroller,
    aforce_data,
    alogin_required,
)


class TestAForceData:
    """Tests for декоратора aforce_data"""

    @pytest.mark.asyncio
    async def test_aforce_data_basic(self):
        """Test базовой функциональности aforce_data"""

        @aforce_data
        async def mock_view(request):
            return HttpResponse('OK')

        # Создаем мок запроса
        request = MagicMock(spec=ASGIRequest)
        request.POST = QueryDict('post_key=post_value')
        request.GET = QueryDict('get_key=get_value')
        request.body = b'{"json_key": "json_value"}'

        response = await mock_view(request)

        assert response.status_code == 200
        assert hasattr(request, 'data')
        assert request.data['post_key'] == 'post_value'
        assert request.data['get_key'] == 'get_value'
        assert request.data['json_key'] == 'json_value'

    @pytest.mark.asyncio
    async def test_aforce_data_invalid_json(self):
        """Test обработки невалидного JSON"""

        @aforce_data
        async def mock_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=ASGIRequest)
        request.POST = QueryDict('post_key=post_value')
        request.GET = QueryDict('get_key=get_value')
        request.body = b'invalid json'

        response = await mock_view(request)

        assert response.status_code == 200
        assert hasattr(request, 'data')
        assert 'json_key' not in request.data
        assert request.data['post_key'] == 'post_value'

    @pytest.mark.asyncio
    async def test_aforce_data_existing_data(self):
        """Test с уже существующим атрибутом data"""

        @aforce_data
        async def mock_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=ASGIRequest)
        request.data = {'existing': 'value'}
        request.POST = QueryDict('post_key=post_value')
        request.GET = QueryDict('get_key=get_value')
        request.body = b'{"json_key": "json_value"}'

        response = await mock_view(request)

        assert response.status_code == 200
        assert request.data['existing'] == 'value'
        assert request.data['post_key'] == 'post_value'


class TestAatomic:
    """Tests for декоратора aatomic"""

    @pytest.mark.asyncio
    @patch("adjango.adecorators.AsyncAtomicContextManager")
    async def test_aatomic_decorator(self, mock_context_manager):
        """Test декоратора aatomic"""

        # Мокаем контекстный менеджер
        mock_cm_instance = AsyncMock()
        mock_context_manager.return_value = mock_cm_instance

        @aatomic
        async def mock_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=ASGIRequest)

        response = await mock_view(request)

        assert response.status_code == 200
        mock_context_manager.assert_called_once()
        mock_cm_instance.__aenter__.assert_called_once()
        mock_cm_instance.__aexit__.assert_called_once()


class TestAcontroller:
    """Tests for декоратора acontroller"""

    @pytest.mark.asyncio
    @patch("adjango.adecorators.logging.getLogger")
    async def test_acontroller_basic(self, mock_get_logger):
        """Test базовой функциональности acontroller"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        @acontroller()
        async def mock_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=ASGIRequest)
        request.method = 'GET'

        with patch.object(settings, 'DEBUG', True):
            response = await mock_view(request)

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("adjango.adecorators.logging.getLogger")
    async def test_acontroller_with_logging(self, mock_get_logger):
        """Test логирования в acontroller"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        @acontroller(name='test_controller', log_name=True, log_time=True)
        async def mock_view(request):
            return HttpResponse('OK')

        request = MagicMock(spec=ASGIRequest)
        request.method = 'POST'

        with patch.object(settings, 'DEBUG', True):
            response = await mock_view(request)

        assert response.status_code == 200
        mock_logger.info.assert_called()

    @pytest.mark.asyncio
    @patch("adjango.adecorators.logging.getLogger")
    @patch("adjango.adecorators.traceback_str")
    async def test_acontroller_exception_handling(self, mock_traceback_str, mock_get_logger):
        """Test обработки исключений в acontroller"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_traceback_str.return_value = "Test traceback"

        @acontroller()
        async def mock_view(request):
            raise ValueError("Test error")

        request = MagicMock(spec=ASGIRequest)
        request.method = "GET"

        with patch.object(settings, "DEBUG", False):
            with pytest.raises(ValueError):
                await mock_view(request)

        mock_logger.critical.assert_called()


class TestAallowedOnly:
    """Tests for декоратора aallowed_only"""

    @pytest.mark.asyncio
    async def test_aallowed_only_allowed_method(self):
        """Test разрешенного метода"""

        @aallowed_only(["GET", "POST"])
        async def mock_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=ASGIRequest)
        request.method = "GET"

        response = await mock_view(request)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_aallowed_only_not_allowed_method(self):
        """Test неразрешенного метода"""

        @aallowed_only(["GET", "POST"])
        async def mock_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=ASGIRequest)
        request.method = "DELETE"

        response = await mock_view(request)

        assert isinstance(response, HttpResponseNotAllowed)
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_aallowed_only_sync_function(self):
        """Test с синхронной функцией"""

        @aallowed_only(["GET"])
        def sync_view(request):
            return HttpResponse("OK")

        request = MagicMock(spec=ASGIRequest)
        request.method = "GET"

        response = await sync_view(request)

        assert response.status_code == 200


class TestAloginRequired:
    """Tests for декоратора alogin_required"""

    @pytest.mark.asyncio
    @patch("adjango.adecorators.auser_passes_test")
    async def test_alogin_required_as_decorator(self, mock_auser_passes_test):
        """Test alogin_required как декоратора"""
        mock_decorator = MagicMock()
        mock_auser_passes_test.return_value = mock_decorator

        @alogin_required
        async def mock_view(request):
            return HttpResponse("OK")

        mock_auser_passes_test.assert_called_once()

    @pytest.mark.asyncio
    @patch("adjango.adecorators.auser_passes_test")
    async def test_alogin_required_as_function(self, mock_auser_passes_test):
        """Test alogin_required как функции"""
        mock_decorator = MagicMock()
        mock_auser_passes_test.return_value = mock_decorator

        async def mock_view(request):
            return HttpResponse("OK")

        decorator = alogin_required(function=None, redirect_field_name="next", login_url="/custom-login/")
        decorated_view = decorator(mock_view)

        mock_auser_passes_test.assert_called_once()
        args, kwargs = mock_auser_passes_test.call_args
        assert kwargs["login_url"] == "/custom-login/"
        assert kwargs["redirect_field_name"] == "next"
