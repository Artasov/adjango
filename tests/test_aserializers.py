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
    """Tests for serializer_errors_to_field_errors function"""

    def test_serializer_errors_to_field_errors_basic(self):
        """Test basic functionality"""
        serializer_errors = {
            "field1": ["Error message 1"],
            "field2": ["Error message 2", "Error message 3"],
        }

        result = serializer_errors_to_field_errors(serializer_errors)

        assert len(result) == 3
        assert result[0] == FieldError(field="field1", message="Error message 1")
        assert result[1] == FieldError(field="field2", message="Error message 2")
        assert result[2] == FieldError(field="field2", message="Error message 3")

    def test_serializer_errors_to_field_errors_empty(self):
        """Test with empty errors"""
        result = serializer_errors_to_field_errors({})
        assert result == []

    def test_serializer_errors_to_field_errors_single_field(self):
        """Test with single field"""
        serializer_errors = {"username": ["This field is required"]}

        result = serializer_errors_to_field_errors(serializer_errors)

        assert len(result) == 1
        assert result[0] == FieldError(
            field="username", message="This field is required"
        )


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestDetailAPIException:
    """Tests for DetailAPIException"""

    def test_detail_api_exception_basic(self):
        """Test basic exception creation"""
        detail = DetailExceptionDict(
            message="Test error",
            fields_errors=[FieldError(field="test", message="Test field error")],
        )

        exception = DetailAPIException(detail=detail)

        assert exception.status_code == status.HTTP_400_BAD_REQUEST
        assert exception.detail == detail

    def test_detail_api_exception_custom_status(self):
        """Test with custom status code"""
        detail = DetailExceptionDict(message="Test error", fields_errors=[])

        exception = DetailAPIException(
            detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        assert exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_detail_api_exception_custom_code(self):
        """Test with custom error code"""
        detail = DetailExceptionDict(message="Test error", fields_errors=[])

        exception = DetailAPIException(detail=detail, code="custom_error")

        # Check that code is set (check via attribute if available)
        if hasattr(exception, "default_code"):
            assert exception.default_code == "custom_error"


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestSerializerErrors:
    """Tests for SerializerErrors"""

    def test_serializer_errors_basic(self):
        """Test basic SerializerErrors creation"""
        serializer_errors = {"field1": ["Error 1"], "field2": ["Error 2"]}

        exception = SerializerErrors(serializer_errors)

        assert exception.status_code == status.HTTP_400_BAD_REQUEST
        assert isinstance(exception.detail, dict)
        assert "message" in exception.detail
        assert "fields_errors" in exception.detail
        assert len(exception.detail["fields_errors"]) == 2

    def test_serializer_errors_custom_message(self):
        """Test with custom message"""
        serializer_errors = {"field1": ["Error 1"]}
        custom_message = "Custom error message"

        exception = SerializerErrors(serializer_errors, message=custom_message)

        assert exception.detail["message"] == custom_message

    def test_serializer_errors_custom_status_code(self):
        """Test with custom status code"""
        serializer_errors = {"field1": ["Error 1"]}

        exception = SerializerErrors(
            serializer_errors, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

        assert exception.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestAListSerializer:
    """Tests for AListSerializer"""

    @pytest.mark.asyncio
    async def test_adata_property(self):
        """Test async data property"""
        from unittest.mock import PropertyMock

        # Create mock child serializer
        child_serializer_class = MagicMock()
        child_instance = MagicMock()

        # Create AsyncMock for adata property that returns coroutine
        async def mock_adata():
            return {"id": 1, "name": "Test"}

        type(child_instance).adata = PropertyMock(return_value=mock_adata())
        child_serializer_class.return_value = child_instance

        # Create mock data
        mock_data = [MagicMock(), MagicMock()]

        # Create AListSerializer with child
        child_mock = MagicMock()
        child_mock.__class__ = child_serializer_class
        serializer = AListSerializer(child=child_mock, context={})
        serializer.instance = mock_data

        result = await serializer.adata

        assert len(result) == 2
        assert child_serializer_class.call_count == 2


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestASerializer:
    """Tests for ASerializer"""

    @pytest.mark.asyncio
    async def test_asave(self):
        """Test async save method"""
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
        """Test successful validation"""
        serializer = ASerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_is_valid = AsyncMock(return_value=True)
            mock_sync_to_async.return_value = mock_async_is_valid

            result = await serializer.ais_valid()

            assert result is True
            mock_async_is_valid.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_ais_valid_with_raise_exception(self):
        """Test validation with raise_exception=True"""
        serializer = ASerializer()

        # Set errors directly in _errors
        serializer._errors = {"field1": ["Error message"]}

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_is_valid = AsyncMock(return_value=False)
            mock_sync_to_async.return_value = mock_async_is_valid

            with pytest.raises(SerializerErrors):
                await serializer.ais_valid(raise_exception=True)

    @pytest.mark.asyncio
    async def test_adata_property(self):
        """Test async data property"""
        serializer = ASerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_lambda = AsyncMock(return_value={"test": "data"})
            mock_sync_to_async.return_value = mock_async_lambda

            result = await serializer.adata

            assert result == {"test": "data"}
            mock_sync_to_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_avalid_data_property(self):
        """Test async validated_data property"""
        serializer = ASerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_lambda = AsyncMock(return_value={"validated": "data"})
            mock_sync_to_async.return_value = mock_async_lambda

            result = await serializer.avalid_data

            assert result == {"validated": "data"}
            mock_sync_to_async.assert_called_once()

    def test_many_init(self):
        """Test many_init method"""
        result = ASerializer.many_init(data=[{"test": 1}, {"test": 2}])

        assert isinstance(result, AListSerializer)
        assert hasattr(result, "child")


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestAModelSerializer:
    """Tests for AModelSerializer"""

    @pytest.mark.asyncio
    async def test_asave(self):
        """Test async save method"""
        serializer = AModelSerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_save = AsyncMock(return_value="saved_model")
            mock_sync_to_async.return_value = mock_async_save

            result = await serializer.asave(commit=True)

            assert result == "saved_model"

    @pytest.mark.asyncio
    async def test_ais_valid_success(self):
        """Test successful async validation"""
        serializer = AModelSerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_is_valid = AsyncMock(return_value=True)
            mock_sync_to_async.return_value = mock_async_is_valid

            result = await serializer.ais_valid()

            assert result is True

    @pytest.mark.asyncio
    async def test_ais_valid_with_exception(self):
        """Test async validation with exception"""
        serializer = AModelSerializer()

        # Set errors directly in _errors
        serializer._errors = {"field1": ["Model error"]}

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_is_valid = AsyncMock(return_value=False)
            mock_sync_to_async.return_value = mock_async_is_valid

            with pytest.raises(SerializerErrors):
                await serializer.ais_valid(raise_exception=True)

    def test_is_valid_sync_with_exception(self):
        """Test sync validation with exception"""
        serializer = AModelSerializer()

        # Set errors directly in _errors
        serializer._errors = {"field1": ["Sync model error"]}

        with patch.object(
            AModelSerializer.__bases__[0], "is_valid", return_value=False
        ):
            with pytest.raises(SerializerErrors):
                serializer.is_valid(raise_exception=True)

    def test_is_valid_sync_success(self):
        """Test successful sync validation"""
        serializer = AModelSerializer()

        with patch.object(AModelSerializer.__bases__[0], "is_valid", return_value=True):
            result = serializer.is_valid()
            assert result is True

    @pytest.mark.asyncio
    async def test_adata_property(self):
        """Test async data property"""
        serializer = AModelSerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_lambda = AsyncMock(return_value={"model": "data"})
            mock_sync_to_async.return_value = mock_async_lambda

            result = await serializer.adata

            assert result == {"model": "data"}

    @pytest.mark.asyncio
    async def test_avalid_data_property(self):
        """Test async validated_data property"""
        serializer = AModelSerializer()

        with patch("adjango.aserializers.sync_to_async") as mock_sync_to_async:
            mock_async_lambda = AsyncMock(return_value={"validated_model": "data"})
            mock_sync_to_async.return_value = mock_async_lambda

            result = await serializer.avalid_data

            assert result == {"validated_model": "data"}

    @patch("adjango.aserializers.LIST_SERIALIZER_KWARGS", ["allow_empty"])
    @patch("adjango.aserializers.LIST_SERIALIZER_KWARGS_REMOVE", ["many"])
    def test_many_init_with_custom_list_serializer(self):
        """Test many_init with custom list serializer"""

        class CustomListSerializer(AListSerializer):
            pass

        class TestModelSerializer(AModelSerializer):
            class Meta:
                model = User
                fields = "__all__"
                list_serializer_class = CustomListSerializer

        result = TestModelSerializer.many_init(
            data=[{"test": 1}], many=True, allow_empty=False
        )

        assert isinstance(result, CustomListSerializer)

    def test_many_init_default(self):
        """Test many_init with default settings"""
        result = AModelSerializer.many_init(data=[{"test": 1}])

        assert isinstance(result, AListSerializer)


@pytest.mark.skipif(DRF_AVAILABLE, reason="Skip when DRF is available")
class TestWithoutDRF:
    """Tests when Django REST Framework is unavailable"""

    def test_import_without_drf(self):
        """Test module import without DRF"""
        # Main functions should be available even without DRF
        from adjango.aserializers import FieldError, serializer_errors_to_field_errors

        assert FieldError is not None
        assert serializer_errors_to_field_errors is not None

        # Test basic functionality without DRF
        result = serializer_errors_to_field_errors({"field": ["error"]})
        assert len(result) == 1
