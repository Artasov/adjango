# test_exceptions.py
import pytest

try:
    from rest_framework.exceptions import APIException
    from rest_framework.status import (
        HTTP_400_BAD_REQUEST,
        HTTP_403_FORBIDDEN,
        HTTP_404_NOT_FOUND,
        HTTP_409_CONFLICT,
    )

    DRF_AVAILABLE = True
except ImportError:
    DRF_AVAILABLE = False

from adjango.exceptions.base import ModelApiBaseException


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestModelApiBaseException:
    """Тесты для ModelApiBaseException"""

    def test_basic_api_exceptions(self):
        """Тест базовых API исключений"""

        class TestModel(ModelApiBaseException):
            pass

        # Проверяем, что все базовые исключения доступны
        assert hasattr(TestModel.ApiEx, "DoesNotExist")
        assert hasattr(TestModel.ApiEx, "AlreadyExists")
        assert hasattr(TestModel.ApiEx, "InvalidData")
        assert hasattr(TestModel.ApiEx, "AccessDenied")
        assert hasattr(TestModel.ApiEx, "NotAcceptable")
        assert hasattr(TestModel.ApiEx, "InternalServerError")

        # Проверяем дополнительные исключения
        assert hasattr(TestModel.ApiEx, "AlreadyUsed")
        assert hasattr(TestModel.ApiEx, "NotUsed")
        assert hasattr(TestModel.ApiEx, "NotAvailable")
        assert hasattr(TestModel.ApiEx, "TemporarilyUnavailable")
        assert hasattr(TestModel.ApiEx, "ConflictDetected")
        assert hasattr(TestModel.ApiEx, "LimitExceeded")
        assert hasattr(TestModel.ApiEx, "DependencyMissing")
        assert hasattr(TestModel.ApiEx, "Expired")

    def test_does_not_exist_exception(self):
        """Тест исключения DoesNotExist"""

        class TestModel(ModelApiBaseException):
            pass

        exception = TestModel.ApiEx.DoesNotExist()
        assert exception.status_code == HTTP_404_NOT_FOUND
        assert "TestModel" in str(exception.default_detail)
        assert exception.default_code == "testmodel_does_not_exist"

    def test_already_exists_exception(self):
        """Тест исключения AlreadyExists"""

        class TestModel(ModelApiBaseException):
            pass

        exception = TestModel.ApiEx.AlreadyExists()
        assert exception.status_code == HTTP_409_CONFLICT
        assert "TestModel" in str(exception.default_detail)
        assert exception.default_code == "testmodel_already_exists"

    def test_invalid_data_exception(self):
        """Тест исключения InvalidData"""

        class TestModel(ModelApiBaseException):
            pass

        exception = TestModel.ApiEx.InvalidData()
        assert exception.status_code == HTTP_400_BAD_REQUEST
        assert "TestModel" in str(exception.default_detail)
        assert exception.default_code == "testmodel_invalid_data"

    def test_access_denied_exception(self):
        """Тест исключения AccessDenied"""

        class TestModel(ModelApiBaseException):
            pass

        exception = TestModel.ApiEx.AccessDenied()
        assert exception.status_code == HTTP_403_FORBIDDEN
        assert "TestModel" in str(exception.default_detail)
        assert exception.default_code == "testmodel_access_denied"

    def test_custom_api_exceptions(self):
        """Тест кастомных API исключений"""

        class TestModel(ModelApiBaseException):
            class ApiEx:
                class CustomException(APIException):
                    status_code = HTTP_400_BAD_REQUEST
                    default_detail = {"message": "Custom exception"}
                    default_code = "custom_exception"

        # Проверяем, что кастомное исключение доступно
        assert hasattr(TestModel.ApiEx, "CustomException")
        assert hasattr(TestModel.ApiEx, "DoesNotExist")  # Базовые тоже должны быть

        exception = TestModel.ApiEx.CustomException()
        assert exception.status_code == HTTP_400_BAD_REQUEST
        assert exception.default_detail == {"message": "Custom exception"}

    def test_multiple_models_different_exceptions(self):
        """Тест разных исключений для разных моделей"""

        class ModelA(ModelApiBaseException):
            pass

        class ModelB(ModelApiBaseException):
            pass

        # Проверяем, что исключения для разных моделей имеют разные сообщения
        exception_a = ModelA.ApiEx.DoesNotExist()
        exception_b = ModelB.ApiEx.DoesNotExist()

        assert "ModelA" in str(exception_a.default_detail)
        assert "ModelB" in str(exception_b.default_detail)
        assert exception_a.default_code == "modela_does_not_exist"
        assert exception_b.default_code == "modelb_does_not_exist"

    def test_inheritance_with_custom_exceptions(self):
        """Тест наследования с кастомными исключениями"""

        class BaseModel(ModelApiBaseException):
            class ApiEx:
                class BaseCustomException(APIException):
                    status_code = HTTP_400_BAD_REQUEST
                    default_detail = {"message": "Base custom exception"}

        class ChildModel(BaseModel):
            class ApiEx:
                class ChildCustomException(APIException):
                    status_code = HTTP_400_BAD_REQUEST
                    default_detail = {"message": "Child custom exception"}

        # Проверяем, что у дочерней модели есть свои исключения
        assert hasattr(ChildModel.ApiEx, "ChildCustomException")
        assert hasattr(ChildModel.ApiEx, "DoesNotExist")  # Базовые должны быть

    def test_exception_instantiation_with_custom_detail(self):
        """Тест создания исключения с кастомным сообщением"""

        class TestModel(ModelApiBaseException):
            pass

        custom_detail = {"message": "Custom error message"}
        exception = TestModel.ApiEx.DoesNotExist(detail=custom_detail)

        assert exception.detail == custom_detail

    def test_all_additional_exceptions(self):
        """Тест всех дополнительных исключений"""

        class TestModel(ModelApiBaseException):
            pass

        additional_exceptions = [
            "AlreadyUsed",
            "NotUsed",
            "NotAvailable",
            "TemporarilyUnavailable",
            "ConflictDetected",
            "LimitExceeded",
            "DependencyMissing",
            "Expired",
        ]

        for exc_name in additional_exceptions:
            assert hasattr(TestModel.ApiEx, exc_name)
            exception_class = getattr(TestModel.ApiEx, exc_name)
            exception = exception_class()
            assert isinstance(exception, APIException)
            assert "TestModel" in str(exception.default_detail)

    def test_descriptor_behavior(self):
        """Тест поведения дескриптора"""

        class TestModel(ModelApiBaseException):
            pass

        # Проверяем, что ApiEx - это дескриптор
        assert hasattr(TestModel, "ApiEx")

        # Каждый доступ должен возвращать новый класс с правильными исключениями
        api_ex_1 = TestModel.ApiEx
        api_ex_2 = TestModel.ApiEx

        # Должны быть одинаковыми по функциональности
        assert hasattr(api_ex_1, "DoesNotExist")
        assert hasattr(api_ex_2, "DoesNotExist")


@pytest.mark.skipif(DRF_AVAILABLE, reason="Skip when DRF is available")
class TestWithoutDRF:
    """Тесты когда Django REST Framework недоступен"""

    def test_import_without_drf(self):
        """Тест импорта модуля без DRF"""
        # Модуль должен импортироваться даже без DRF
        from adjango.exceptions.base import ModelApiBaseException

        assert ModelApiBaseException is not None
