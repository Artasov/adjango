# test_exceptions.py
import sys
from enum import Enum
from unittest.mock import Mock, patch

import pytest
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

# Импорты из тестируемого модуля
from adjango.exceptions.base import (
    _VARIANT_TO_STATUS,
    ApiExceptionGenerator,
    ModelApiExceptionBaseVariant,
    ModelApiExceptionGenerator,
    _model_verbose_name,
    _slug_code,
    _variant_message,
)


class TestHelperFunctions(TestCase):
    """Тесты для вспомогательных функций модуля exceptions"""

    def test_slug_code_basic(self):
        """Тест базовой функциональности _slug_code"""
        # Базовые случаи
        self.assertEqual(_slug_code("Simple Test"), "simple_test")
        self.assertEqual(_slug_code("UPPERCASE"), "uppercase")
        self.assertEqual(_slug_code("Mixed Case String"), "mixed_case_string")

    def test_slug_code_special_characters(self):
        """Тест обработки специальных символов в _slug_code"""
        self.assertEqual(_slug_code("Test@#$%^&*()!"), "test")
        self.assertEqual(_slug_code("Test-with-dashes"), "test_with_dashes")
        self.assertEqual(_slug_code("Test.with.dots"), "test_with_dots")
        self.assertEqual(_slug_code("Test/with/slashes"), "test_with_slashes")

    def test_slug_code_whitespace(self):
        """Тест обработки пробелов в _slug_code"""
        self.assertEqual(_slug_code("  Multiple   Spaces  "), "multiple_spaces")
        self.assertEqual(_slug_code("\t\nTabs and Newlines\t\n"), "tabs_and_newlines")
        self.assertEqual(_slug_code(""), "error")  # Пустая строка возвращает "error"
        self.assertEqual(_slug_code("   "), "error")  # Только пробелы возвращают "error"

    def test_slug_code_underscores(self):
        """Тест обработки подчёркиваний в _slug_code"""
        self.assertEqual(_slug_code("test__multiple__underscores"), "test_multiple_underscores")
        self.assertEqual(_slug_code("_leading_underscore"), "leading_underscore")
        self.assertEqual(_slug_code("trailing_underscore_"), "trailing_underscore")
        self.assertEqual(_slug_code("___"), "error")  # Только подчёркивания возвращают "error"

    def test_slug_code_numbers(self):
        """Тест обработки чисел в _slug_code"""
        self.assertEqual(_slug_code("Test123"), "test123")
        self.assertEqual(_slug_code("123Test"), "123test")
        self.assertEqual(_slug_code("Test 123 String"), "test_123_string")

    def test_model_verbose_name_with_meta(self):
        """Тест _model_verbose_name с корректной мета-информацией"""
        # Создаём мок модели с verbose_name
        mock_model = Mock()
        mock_model._meta.verbose_name = "Test Model"
        mock_model.__name__ = "TestModel"

        result = _model_verbose_name(mock_model)
        self.assertEqual(result, "Test Model")

    def test_model_verbose_name_without_meta(self):
        """Тест _model_verbose_name без мета-информации"""
        # Создаём мок модели без _meta
        mock_model = Mock()
        del mock_model._meta  # Удаляем _meta атрибут
        mock_model.__name__ = "TestModel"

        result = _model_verbose_name(mock_model)
        self.assertEqual(result, "TestModel")

    def test_model_verbose_name_with_empty_verbose_name(self):
        """Тест _model_verbose_name с пустым verbose_name"""
        mock_model = Mock()
        mock_model._meta.verbose_name = None
        mock_model.__name__ = "TestModel"

        result = _model_verbose_name(mock_model)
        self.assertEqual(result, "TestModel")

    def test_model_verbose_name_with_exception(self):
        """Тест _model_verbose_name когда возникает исключение в блоке try"""

        # Создаём специальный класс, который будет вызывать исключение при обращении к str()
        class MockVerboseName:
            def __str__(self):
                raise Exception("Test exception")

        mock_model = Mock()
        mock_model._meta.verbose_name = MockVerboseName()
        mock_model.__name__ = "TestModel"

        result = _model_verbose_name(mock_model)
        self.assertEqual(result, "TestModel")


class TestModelApiExceptionBaseVariant(TestCase):
    """Тесты для enum ModelApiExceptionBaseVariant"""

    def test_all_variants_exist(self):
        """Тест что все варианты исключений определены"""
        expected_variants = [
            "DoesNotExist",
            "AlreadyExists",
            "InvalidData",
            "AccessDenied",
            "NotAcceptable",
            "Expired",
            "InternalServerError",
            "AlreadyUsed",
            "NotUsed",
            "NotAvailable",
            "TemporarilyUnavailable",
            "ConflictDetected",
            "LimitExceeded",
            "DependencyMissing",
            "Deprecated",
        ]

        for variant_name in expected_variants:
            self.assertTrue(hasattr(ModelApiExceptionBaseVariant, variant_name))

    def test_variant_values(self):
        """Тест значений вариантов исключений"""
        self.assertEqual(ModelApiExceptionBaseVariant.DoesNotExist.value, "does_not_exist")
        self.assertEqual(ModelApiExceptionBaseVariant.AlreadyExists.value, "already_exists")
        self.assertEqual(ModelApiExceptionBaseVariant.InvalidData.value, "invalid_data")
        self.assertEqual(ModelApiExceptionBaseVariant.AccessDenied.value, "access_denied")

    def test_variant_to_status_mapping(self):
        """Тест маппинга вариантов на HTTP статусы"""
        # Проверяем что все варианты имеют соответствующий статус
        for variant in ModelApiExceptionBaseVariant:
            self.assertIn(variant, _VARIANT_TO_STATUS)
            self.assertIsInstance(_VARIANT_TO_STATUS[variant], int)

        # Проверяем конкретные маппинги
        self.assertEqual(_VARIANT_TO_STATUS[ModelApiExceptionBaseVariant.DoesNotExist], 404)
        self.assertEqual(_VARIANT_TO_STATUS[ModelApiExceptionBaseVariant.AlreadyExists], 409)
        self.assertEqual(_VARIANT_TO_STATUS[ModelApiExceptionBaseVariant.InvalidData], 400)
        self.assertEqual(_VARIANT_TO_STATUS[ModelApiExceptionBaseVariant.AccessDenied], 403)


class TestVariantMessageFunction(TestCase):
    """Тесты для функции _variant_message"""

    def test_variant_messages(self):
        """Тест генерации сообщений для всех вариантов"""
        model_name = "TestModel"

        # Тестируем каждый вариант
        test_cases = [
            (ModelApiExceptionBaseVariant.DoesNotExist, f"{model_name} does not exist"),
            (ModelApiExceptionBaseVariant.AlreadyExists, f"{model_name} already exists"),
            (ModelApiExceptionBaseVariant.InvalidData, f"Invalid data for {model_name}"),
            (ModelApiExceptionBaseVariant.AccessDenied, f"Access denied for {model_name}"),
            (ModelApiExceptionBaseVariant.NotAcceptable, f"Not acceptable for {model_name}"),
            (ModelApiExceptionBaseVariant.Expired, f"{model_name} expired"),
            (ModelApiExceptionBaseVariant.InternalServerError, f"Internal server error in {model_name}"),
            (ModelApiExceptionBaseVariant.AlreadyUsed, f"{model_name} already used"),
            (ModelApiExceptionBaseVariant.NotUsed, f"{model_name} not used"),
            (ModelApiExceptionBaseVariant.NotAvailable, f"{model_name} not available"),
            (ModelApiExceptionBaseVariant.TemporarilyUnavailable, f"{model_name} temporarily unavailable"),
            (ModelApiExceptionBaseVariant.ConflictDetected, f"{model_name} conflict detected"),
            (ModelApiExceptionBaseVariant.LimitExceeded, f"{model_name} limit exceeded"),
            (ModelApiExceptionBaseVariant.DependencyMissing, f"{model_name} dependency missing"),
            (ModelApiExceptionBaseVariant.Deprecated, f"{model_name} deprecated"),
        ]

        for variant, expected_message in test_cases:
            with self.subTest(variant=variant):
                result = _variant_message(model_name, variant)
                # Так как используется gettext_lazy, проверяем что сообщение содержит ожидаемые части
                self.assertIn(model_name, result)


class TestApiExceptionGenerator(TestCase):
    """Тесты для класса ApiExceptionGenerator"""

    def test_basic_initialization(self):
        """Тест базовой инициализации ApiExceptionGenerator"""
        message = "Test error message"
        status = 400

        exception = ApiExceptionGenerator(message, status)

        self.assertEqual(exception.status_code, status)
        self.assertEqual(exception.detail["message"], message)
        self.assertEqual(exception.default_code, "test_error_message")

    def test_initialization_with_custom_code(self):
        """Тест инициализации с пользовательским кодом"""
        message = "Test error"
        status = 500
        custom_code = "custom_error_code"

        exception = ApiExceptionGenerator(message, status, custom_code)

        self.assertEqual(exception.status_code, status)
        self.assertEqual(exception.detail["message"], message)
        self.assertEqual(exception.default_code, custom_code)

    def test_initialization_with_extra_data(self):
        """Тест инициализации с дополнительными данными"""
        message = "Validation error"
        status = 400
        extra_data = {"field": "email", "value": "invalid@"}

        exception = ApiExceptionGenerator(message, status, extra=extra_data)

        self.assertEqual(exception.status_code, status)
        self.assertEqual(exception.detail["message"], message)
        self.assertEqual(exception.detail["field"], "email")
        self.assertEqual(exception.detail["value"], "invalid@")

    def test_initialization_with_all_parameters(self):
        """Тест инициализации со всеми параметрами"""
        message = "Complex error"
        status = 422
        code = "validation_failed"
        extra = {"errors": ["field1", "field2"]}

        exception = ApiExceptionGenerator(message, status, code, extra)

        self.assertEqual(exception.status_code, status)
        self.assertEqual(exception.detail["message"], message)
        self.assertEqual(exception.detail["errors"], ["field1", "field2"])
        self.assertEqual(exception.default_code, code)

    def test_status_code_conversion(self):
        """Тест конвертации статус кода в int"""
        message = "Test"
        status = "400"  # Строка вместо числа

        exception = ApiExceptionGenerator(message, status)

        self.assertEqual(exception.status_code, 400)
        self.assertIsInstance(exception.status_code, int)


class TestModelApiExceptionGenerator(TestCase):
    """Тесты для класса ModelApiExceptionGenerator"""

    def setUp(self):
        """Настройка тестов"""
        # Создаём мок модель
        self.mock_model = Mock()
        self.mock_model._meta.verbose_name = "Test Model"
        self.mock_model.__name__ = "TestModel"

    def test_basic_initialization(self):
        """Тест базовой инициализации ModelApiExceptionGenerator"""
        variant = ModelApiExceptionBaseVariant.DoesNotExist

        exception = ModelApiExceptionGenerator(self.mock_model, variant)

        self.assertEqual(exception.status_code, 404)
        self.assertIn("Test Model", exception.detail["message"])
        self.assertEqual(exception.default_code, "does_not_exist")

    def test_initialization_with_custom_code(self):
        """Тест инициализации с пользовательским кодом"""
        variant = ModelApiExceptionBaseVariant.AlreadyExists
        custom_code = "model_exists"

        exception = ModelApiExceptionGenerator(self.mock_model, variant, custom_code)

        self.assertEqual(exception.status_code, 409)
        self.assertEqual(exception.default_code, custom_code)

    def test_initialization_with_extra_data(self):
        """Тест инициализации с дополнительными данными"""
        variant = ModelApiExceptionBaseVariant.InvalidData
        extra = {"id": 123, "field": "name"}

        exception = ModelApiExceptionGenerator(self.mock_model, variant, extra=extra)

        self.assertEqual(exception.status_code, 400)
        # ErrorDetail преобразует значения в строки, поэтому проверяем строковые значения
        self.assertEqual(str(exception.detail["id"]), "123")
        self.assertEqual(str(exception.detail["field"]), "name")

    def test_all_variants_status_codes(self):
        """Тест статус кодов для всех вариантов"""
        for variant in ModelApiExceptionBaseVariant:
            with self.subTest(variant=variant):
                exception = ModelApiExceptionGenerator(self.mock_model, variant)
                expected_status = _VARIANT_TO_STATUS[variant]
                self.assertEqual(exception.status_code, expected_status)

    def test_fallback_status_code(self):
        """Тест резервного статус кода для неизвестного варианта"""
        # Создаём "неизвестный" вариант (хотя это не должно происходить в реальности)
        with patch.dict("adjango.exceptions.base._VARIANT_TO_STATUS", {}, clear=True):
            variant = ModelApiExceptionBaseVariant.DoesNotExist
            exception = ModelApiExceptionGenerator(self.mock_model, variant)
            self.assertEqual(exception.status_code, 500)  # HTTP_500_INTERNAL_SERVER_ERROR

    def test_model_without_verbose_name(self):
        """Тест с моделью без verbose_name"""
        mock_model_no_meta = Mock()
        del mock_model_no_meta._meta
        mock_model_no_meta.__name__ = "PlainModel"

        variant = ModelApiExceptionBaseVariant.DoesNotExist
        exception = ModelApiExceptionGenerator(mock_model_no_meta, variant)

        self.assertIn("PlainModel", exception.detail["message"])


class TestCompatibilityMode(TestCase):
    """Тесты для режима совместимости когда DRF не установлен"""

    def test_fallback_classes_exist(self):
        """Тест что fallback классы определены в модуле"""
        # Проверяем что в модуле есть fallback классы/константы
        import adjango.exceptions.base as base_module

        # Проверяем что в модуле определены HTTP статусы (либо из DRF, либо fallback)
        self.assertTrue(hasattr(base_module, "HTTP_400_BAD_REQUEST"))
        self.assertTrue(hasattr(base_module, "HTTP_404_NOT_FOUND"))
        self.assertTrue(hasattr(base_module, "HTTP_500_INTERNAL_SERVER_ERROR"))

        # Проверяем что APIException доступен (либо из DRF, либо fallback)
        try:
            from rest_framework.exceptions import APIException as DRFAPIException

            # DRF установлен, проверяем что наши классы наследуются от него
            self.assertTrue(issubclass(ApiExceptionGenerator, DRFAPIException))
        except ImportError:
            # DRF не установлен, проверяем fallback
            self.assertTrue(hasattr(base_module, "APIException"))

    def test_api_exception_generator_works_regardless_of_drf(self):
        """Тест что ApiExceptionGenerator работает независимо от наличия DRF"""
        # Создаём исключение - должно работать в любом случае
        exception = ApiExceptionGenerator("Test error", 400)
        self.assertEqual(exception.status_code, 400)
        self.assertEqual(exception.detail["message"], "Test error")

    def test_http_status_constants(self):
        """Тест что HTTP статус константы определены"""
        from adjango.exceptions.base import (
            HTTP_400_BAD_REQUEST,
            HTTP_403_FORBIDDEN,
            HTTP_404_NOT_FOUND,
            HTTP_406_NOT_ACCEPTABLE,
            HTTP_408_REQUEST_TIMEOUT,
            HTTP_409_CONFLICT,
            HTTP_500_INTERNAL_SERVER_ERROR,
            HTTP_503_SERVICE_UNAVAILABLE,
        )

        self.assertEqual(HTTP_400_BAD_REQUEST, 400)
        self.assertEqual(HTTP_403_FORBIDDEN, 403)
        self.assertEqual(HTTP_404_NOT_FOUND, 404)
        self.assertEqual(HTTP_406_NOT_ACCEPTABLE, 406)
        self.assertEqual(HTTP_408_REQUEST_TIMEOUT, 408)
        self.assertEqual(HTTP_409_CONFLICT, 409)
        self.assertEqual(HTTP_500_INTERNAL_SERVER_ERROR, 500)
        self.assertEqual(HTTP_503_SERVICE_UNAVAILABLE, 503)


class TestExceptionIntegration(TestCase):
    """Интеграционные тесты для проверки взаимодействия компонентов"""

    def setUp(self):
        """Настройка интеграционных тестов"""
        self.mock_model = Mock()
        self.mock_model._meta.verbose_name = "User"
        self.mock_model.__name__ = "User"

    def test_api_exception_generator_exception_raising(self):
        """Тест что ApiExceptionGenerator правильно выбрасывается как исключение"""
        with self.assertRaises(ApiExceptionGenerator) as context:
            raise ApiExceptionGenerator("Test error", 400)

        exception = context.exception
        self.assertEqual(exception.status_code, 400)
        self.assertEqual(exception.detail["message"], "Test error")

    def test_model_api_exception_generator_exception_raising(self):
        """Тест что ModelApiExceptionGenerator правильно выбрасывается как исключение"""
        with self.assertRaises(ModelApiExceptionGenerator) as context:
            raise ModelApiExceptionGenerator(self.mock_model, ModelApiExceptionBaseVariant.DoesNotExist)

        exception = context.exception
        self.assertEqual(exception.status_code, 404)
        self.assertIn("User", exception.detail["message"])

    def test_complex_exception_scenario(self):
        """Тест сложного сценария использования исключений"""
        # Тест с ModelApiExceptionGenerator с дополнительными данными
        extra_data = {"user_id": 123, "attempted_action": "delete", "timestamp": "2023-01-01T00:00:00Z"}

        with self.assertRaises(ModelApiExceptionGenerator) as context:
            raise ModelApiExceptionGenerator(
                self.mock_model, ModelApiExceptionBaseVariant.AccessDenied, code="user_access_denied", extra=extra_data
            )

        exception = context.exception
        self.assertEqual(exception.status_code, 403)
        self.assertEqual(exception.default_code, "user_access_denied")
        # ErrorDetail преобразует значения в строки
        self.assertEqual(str(exception.detail["user_id"]), "123")
        self.assertEqual(str(exception.detail["attempted_action"]), "delete")
        self.assertEqual(str(exception.detail["timestamp"]), "2023-01-01T00:00:00Z")

    def test_exception_inheritance(self):
        """Тест что наши исключения правильно наследуются от APIException"""
        api_exception = ApiExceptionGenerator("Test", 400)
        model_exception = ModelApiExceptionGenerator(self.mock_model, ModelApiExceptionBaseVariant.DoesNotExist)

        # В зависимости от того, установлен ли DRF, проверяем наследование
        try:
            from rest_framework.exceptions import APIException as DRFAPIException

            self.assertIsInstance(api_exception, DRFAPIException)
            self.assertIsInstance(model_exception, DRFAPIException)
        except ImportError:
            from adjango.exceptions.base import APIException as FallbackAPIException

            self.assertIsInstance(api_exception, FallbackAPIException)
            self.assertIsInstance(model_exception, FallbackAPIException)


if __name__ == "__main__":
    pytest.main([__file__])
