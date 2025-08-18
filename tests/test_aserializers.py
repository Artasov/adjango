# test_aserializers.py
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from django.contrib.auth.models import User
    from rest_framework import status
    from rest_framework.exceptions import APIException
    from rest_framework.serializers import ModelSerializer, Serializer

    DRF_AVAILABLE = True
except ImportError:
    DRF_AVAILABLE = False

from adjango.aserializers import (
    AListSerializer,
    AModelSerializer,
    ASerializer,
    DetailAPIException,
    DetailExceptionDict,
    FieldError,
    SerializerErrors,
    serializer_errors_to_field_errors,
)


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestFieldErrorsFunction:
    """Тесты для функции serializer_errors_to_field_errors"""

    def test_serializer_errors_to_field_errors_basic(self):
        """Тест базовой функциональности"""
        serializer_errors = {"field1": ["Error message 1"], "field2": ["Error message 2", "Error message 3"]}

        result = serializer_errors_to_field_errors(serializer_errors)

        assert len(result) == 3
        assert result[0] == FieldError(field="field1", message="Error message 1")
        assert result[1] == FieldError(field="field2", message="Error message 2")
        assert result[2] == FieldError(field="field2", message="Error message 3")

    def test_serializer_errors_to_field_errors_empty(self):
        """Тест с пустыми ошибками"""
        result = serializer_errors_to_field_errors({})
        assert result == []

    def test_serializer_errors_to_field_errors_single_field(self):
        """Тест с одним полем"""
        serializer_errors = {"username": ["This field is required"]}

        result = serializer_errors_to_field_errors(serializer_errors)

        assert len(result) == 1
        assert result[0] == FieldError(field="username", message="This field is required")


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestDetailAPIException:
    """Тесты для DetailAPIException"""

    def test_detail_api_exception_basic(self):
        """Тест базового создания исключения"""
        detail = DetailExceptionDict(
            message="Test error", fields_errors=[FieldError(field="test", message="Test field error")]
        )

        exception = DetailAPIException(detail=detail)

        assert exception.status_code == status.HTTP_400_BAD_REQUEST
        assert exception.detail == detail

    def test_detail_api_exception_custom_status(self):
        """Тест с кастомным статус кодом"""
        detail = DetailExceptionDict(message="Test error", fields_errors=[])

        exception = DetailAPIException(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        assert exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_detail_api_exception_custom_code(self):
        """Тест с кастомным кодом ошибки"""
        detail = DetailExceptionDict(message="Test error", fields_errors=[])

        exception = DetailAPIException(detail=detail, code="custom_error")

        # Проверяем что код установлен (проверяем через атрибут, если доступен)
        if hasattr(exception, "default_code"):
            assert exception.default_code == "custom_error"


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestSerializerErrors:
    """Тесты для SerializerErrors"""

    def test_serializer_errors_basic(self):
        """Тест базового создания SerializerErrors"""
        serializer_errors = {"field1": ["Error 1"], "field2": ["Error 2"]}

        exception = SerializerErrors(serializer_errors)

        assert exception.status_code == status.HTTP_400_BAD_REQUEST
        assert isinstance(exception.detail, dict)
        assert "message" in exception.detail
        assert "fields_errors" in exception.detail
        assert len(exception.detail["fields_errors"]) == 2

    def test_serializer_errors_custom_message(self):
        """Тест с кастомным сообщением"""
        serializer_errors = {"field1": ["Error 1"]}
        custom_message = "Custom error message"

        exception = SerializerErrors(serializer_errors, message=custom_message)

        assert exception.detail["message"] == custom_message

    def test_serializer_errors_custom_status_code(self):
        """Тест с кастомным статус кодом"""
        serializer_errors = {"field1": ["Error 1"]}

        exception = SerializerErrors(serializer_errors, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

        assert exception.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestAListSerializer:
    """Тесты для AListSerializer"""

    @pytest.mark.asyncio
    async def test_adata_property(self):
        """Тест async свойства data"""
        from unittest.mock import PropertyMock

        # Создаем мок дочернего сериализатора
        child_serializer_class = MagicMock()
        child_instance = MagicMock()

        # Создаем AsyncMock для свойства adata, который возвращает корутину
        async def mock_adata():
            return {"id": 1, "name": "Test"}

        type(child_instance).adata = PropertyMock(return_value=mock_adata())
        child_serializer_class.return_value = child_instance

        # Создаем мок данных
        mock_data = [MagicMock(), MagicMock()]

        # Создаем AListSerializer с child
        child_mock = MagicMock()
        child_mock.__class__ = child_serializer_class
        serializer = AListSerializer(child=child_mock, context={})
        serializer.instance = mock_data

        result = await serializer.adata

        assert len(result) == 2
        assert child_serializer_class.call_count == 2


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestASerializer:
    """Тесты для ASerializer"""

    @pytest.mark.asyncio
    async def test_asave(self):
        """Тест async метода save"""
        serializer = ASerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_save = AsyncMock(return_value="saved_instance")
            mock_sync_to_async.return_value = mock_async_save

            result = await serializer.asave(test_kwarg="test_value")

            mock_sync_to_async.assert_called_once_with(serializer.save)
            mock_async_save.assert_called_once_with(test_kwarg="test_value")
            assert result == "saved_instance"

    @pytest.mark.asyncio
    async def test_ais_valid_success(self):
        """Тест успешной валидации"""
        serializer = ASerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_is_valid = AsyncMock(return_value=True)
            mock_sync_to_async.return_value = mock_async_is_valid

            result = await serializer.ais_valid()

            assert result is True
            mock_async_is_valid.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_ais_valid_with_raise_exception(self):
        """Тест валидации с raise_exception=True"""
        serializer = ASerializer()

        # Устанавливаем ошибки напрямую в _errors
        serializer._errors = {"field1": ["Error message"]}

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_is_valid = AsyncMock(return_value=False)
            mock_sync_to_async.return_value = mock_async_is_valid

            with pytest.raises(SerializerErrors):
                await serializer.ais_valid(raise_exception=True)

    @pytest.mark.asyncio
    async def test_adata_property(self):
        """Тест async свойства data"""
        serializer = ASerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_lambda = AsyncMock(return_value={"test": "data"})
            mock_sync_to_async.return_value = mock_async_lambda

            result = await serializer.adata

            assert result == {"test": "data"}
            mock_sync_to_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_avalid_data_property(self):
        """Тест async свойства validated_data"""
        serializer = ASerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_lambda = AsyncMock(return_value={"validated": "data"})
            mock_sync_to_async.return_value = mock_async_lambda

            result = await serializer.avalid_data

            assert result == {"validated": "data"}
            mock_sync_to_async.assert_called_once()

    def test_many_init(self):
        """Тест many_init метода"""
        result = ASerializer.many_init(data=[{"test": 1}, {"test": 2}])

        assert isinstance(result, AListSerializer)
        assert hasattr(result, "child")


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestAModelSerializer:
    """Тесты для AModelSerializer"""

    @pytest.mark.asyncio
    async def test_asave(self):
        """Тест async метода save"""
        serializer = AModelSerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_save = AsyncMock(return_value="saved_model")
            mock_sync_to_async.return_value = mock_async_save

            result = await serializer.asave(commit=True)

            assert result == "saved_model"

    @pytest.mark.asyncio
    async def test_ais_valid_success(self):
        """Тест успешной async валидации"""
        serializer = AModelSerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_is_valid = AsyncMock(return_value=True)
            mock_sync_to_async.return_value = mock_async_is_valid

            result = await serializer.ais_valid()

            assert result is True

    @pytest.mark.asyncio
    async def test_ais_valid_with_exception(self):
        """Тест async валидации с исключением"""
        serializer = AModelSerializer()

        # Устанавливаем ошибки напрямую в _errors
        serializer._errors = {"field1": ["Model error"]}

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_is_valid = AsyncMock(return_value=False)
            mock_sync_to_async.return_value = mock_async_is_valid

            with pytest.raises(SerializerErrors):
                await serializer.ais_valid(raise_exception=True)

    def test_is_valid_sync_with_exception(self):
        """Тест sync валидации с исключением"""
        serializer = AModelSerializer()

        # Устанавливаем ошибки напрямую в _errors
        serializer._errors = {"field1": ["Sync model error"]}

        with patch.object(AModelSerializer.__bases__[0], "is_valid", return_value=False):
            with pytest.raises(SerializerErrors):
                serializer.is_valid(raise_exception=True)

    def test_is_valid_sync_success(self):
        """Тест успешной sync валидации"""
        serializer = AModelSerializer()

        with patch.object(AModelSerializer.__bases__[0], "is_valid", return_value=True):
            result = serializer.is_valid()
            assert result is True

    @pytest.mark.asyncio
    async def test_adata_property(self):
        """Тест async свойства data"""
        serializer = AModelSerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_lambda = AsyncMock(return_value={"model": "data"})
            mock_sync_to_async.return_value = mock_async_lambda

            result = await serializer.adata

            assert result == {"model": "data"}

    @pytest.mark.asyncio
    async def test_avalid_data_property(self):
        """Тест async свойства validated_data"""
        serializer = AModelSerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_lambda = AsyncMock(return_value={"validated_model": "data"})
            mock_sync_to_async.return_value = mock_async_lambda

            result = await serializer.avalid_data

            assert result == {"validated_model": "data"}

    @patch("adjango.aserializers.LIST_SERIALIZER_KWARGS", ["allow_empty"])
    @patch("adjango.aserializers.LIST_SERIALIZER_KWARGS_REMOVE", ["many"])
    def test_many_init_with_custom_list_serializer(self):
        """Тест many_init с кастомным list serializer"""

        class CustomListSerializer(AListSerializer):
            pass

        class TestModelSerializer(AModelSerializer):
            class Meta:
                model = User
                fields = "__all__"
                list_serializer_class = CustomListSerializer

        result = TestModelSerializer.many_init(data=[{"test": 1}], many=True, allow_empty=False)

        assert isinstance(result, CustomListSerializer)

    def test_many_init_default(self):
        """Тест many_init с дефолтными настройками"""
        result = AModelSerializer.many_init(data=[{"test": 1}])

        assert isinstance(result, AListSerializer)


@pytest.mark.skipif(DRF_AVAILABLE, reason="Skip when DRF is available")
class TestWithoutDRF:
    """Тесты когда Django REST Framework недоступен"""

    def test_import_without_drf(self):
        """Тест импорта модуля без DRF"""
        # Основные функции должны быть доступны даже без DRF
        from adjango.aserializers import FieldError, serializer_errors_to_field_errors

        assert FieldError is not None
        assert serializer_errors_to_field_errors is not None

        # Тест базовой функциональности без DRF
        result = serializer_errors_to_field_errors({"field": ["error"]})
        assert len(result) == 1
