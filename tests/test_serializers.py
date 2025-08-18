# test_serializers.py
from unittest.mock import MagicMock

import pytest

try:
    from django.contrib.auth.models import User
    from rest_framework.serializers import BaseSerializer, CharField, IntegerField

    DRF_AVAILABLE = True
except ImportError:
    DRF_AVAILABLE = False

from django.db import models

from adjango.aserializers import AModelSerializer
from adjango.serializers import dynamic_serializer


# Простая тестовая модель для избежания проблем с User
class TestModel(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    class Meta:
        app_label = "test_app"


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestDynamicSerializer:
    """Тесты для функции dynamic_serializer"""

    def test_dynamic_serializer_basic(self):
        """Тест базовой функциональности dynamic_serializer"""

        # Создаем базовый сериализатор
        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()
            field2 = IntegerField()
            field3 = CharField()

            class Meta:
                model = User
                fields = ("field1", "field2", "field3")

        # Создаем динамический сериализатор с ограниченными полями
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer, include_fields=("field1", "field2")
        )

        # Проверяем что новый сериализатор создан
        assert DynamicTestSerializer is not None
        assert issubclass(DynamicTestSerializer, BaseTestSerializer)

        # Проверяем Meta класс
        assert hasattr(DynamicTestSerializer, "Meta")
        assert DynamicTestSerializer.Meta.fields == ("field1", "field2")

    def test_dynamic_serializer_with_field_overrides_class(self):
        """Тест dynamic_serializer с переопределением полей через класс"""

        class BaseTestSerializer(AModelSerializer):
            class Meta:
                model = User
                fields = ("username", "email")

        class CustomFieldSerializer(BaseSerializer):
            pass

        # Создаем динамический сериализатор с переопределением поля
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer,
            include_fields=("username", "email"),
            field_overrides={"username": CustomFieldSerializer},
        )

        # Проверяем что поле переопределено
        instance = DynamicTestSerializer()
        assert "username" in instance.fields
        assert isinstance(instance.fields["username"], CustomFieldSerializer)
        assert instance.fields["username"].read_only is True

    def test_dynamic_serializer_with_field_overrides_instance(self):
        """Тест dynamic_serializer с переопределением полей через экземпляр"""

        class BaseTestSerializer(AModelSerializer):
            class Meta:
                model = User
                fields = ("username", "email")

        class CustomFieldSerializer(BaseSerializer):
            pass

        custom_instance = CustomFieldSerializer(read_only=False)

        # Создаем динамический сериализатор с переопределением поля
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer,
            include_fields=("username", "email"),
            field_overrides={"email": custom_instance},
        )

        # Проверяем что поле переопределено
        instance = DynamicTestSerializer()
        assert "email" in instance.fields
        assert instance.fields["email"] is custom_instance
        assert instance.fields["email"].read_only is False

    def test_dynamic_serializer_invalid_field_override(self):
        """Тест dynamic_serializer с невалидным переопределением поля"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()

            class Meta:
                model = User
                fields = ("field1",)

        # Попытка переопределить поле невалидным значением
        with pytest.raises(ValueError, match="Invalid serializer for field 'field1'"):
            dynamic_serializer(
                base_serializer=BaseTestSerializer,
                include_fields=("field1",),
                field_overrides={"field1": "invalid_serializer"},
            )

    def test_dynamic_serializer_no_field_overrides(self):
        """Тест dynamic_serializer без переопределения полей"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()
            field2 = IntegerField()
            field3 = CharField()

            class Meta:
                model = User
                fields = ("field1", "field2", "field3")

        # Создаем динамический сериализатор без переопределений
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer, include_fields=("field1", "field3")
        )

        # Проверяем что сериализатор создан корректно
        assert DynamicTestSerializer is not None
        assert DynamicTestSerializer.Meta.fields == ("field1", "field3")

        # Проверяем что можем создать экземпляр
        instance = DynamicTestSerializer()
        assert instance is not None

    def test_dynamic_serializer_empty_include_fields(self):
        """Тест dynamic_serializer с пустым списком полей"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()

            class Meta:
                model = User
                fields = ("field1",)

        # Создаем динамический сериализатор с пустыми полями
        DynamicTestSerializer = dynamic_serializer(base_serializer=BaseTestSerializer, include_fields=())

        assert DynamicTestSerializer.Meta.fields == ()

    def test_dynamic_serializer_inheritance(self):
        """Тест наследования от базового сериализатора"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()

            class Meta:
                model = User
                fields = ("field1",)

            def custom_method(self):
                return "base_method"

        # Создаем динамический сериализатор
        DynamicTestSerializer = dynamic_serializer(base_serializer=BaseTestSerializer, include_fields=("field1",))

        # Проверяем наследование методов
        instance = DynamicTestSerializer()
        assert hasattr(instance, "custom_method")
        assert instance.custom_method() == "base_method"

    def test_dynamic_serializer_meta_inheritance(self):
        """Тест наследования Meta класса"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()

            class Meta:
                model = User
                fields = ("field1",)
                read_only_fields = ("field1",)
                extra_kwargs = {"field1": {"required": False}}

        # Создаем динамический сериализатор
        DynamicTestSerializer = dynamic_serializer(base_serializer=BaseTestSerializer, include_fields=("field1",))

        # Проверяем наследование атрибутов Meta
        assert hasattr(DynamicTestSerializer.Meta, "read_only_fields")
        assert hasattr(DynamicTestSerializer.Meta, "extra_kwargs")
        assert DynamicTestSerializer.Meta.read_only_fields == ("field1",)

    def test_dynamic_serializer_multiple_field_overrides(self):
        """Тест dynamic_serializer с множественными переопределениями полей"""

        class BaseTestSerializer(AModelSerializer):
            class Meta:
                model = User
                fields = ("username", "email", "first_name")

        class CustomSerializer1(BaseSerializer):
            pass

        class CustomSerializer2(BaseSerializer):
            pass

        custom_instance = CustomSerializer2()

        # Создаем динамический сериализатор с множественными переопределениями
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer,
            include_fields=("username", "email", "first_name"),
            field_overrides={"username": CustomSerializer1, "first_name": custom_instance},
        )

        # Проверяем переопределения
        instance = DynamicTestSerializer()
        assert isinstance(instance.fields["username"], CustomSerializer1)
        assert instance.fields["first_name"] is custom_instance
        # email должно остаться оригинальным - это поле EmailField из User модели
        assert "email" in instance.fields

    def test_dynamic_serializer_return_type(self):
        """Тест типа возвращаемого значения"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()

            class Meta:
                model = User
                fields = ("field1",)

        # Создаем динамический сериализатор
        DynamicTestSerializer = dynamic_serializer(base_serializer=BaseTestSerializer, include_fields=("field1",))

        # Проверяем что возвращается класс
        assert isinstance(DynamicTestSerializer, type)
        assert issubclass(DynamicTestSerializer, BaseTestSerializer)
        assert issubclass(DynamicTestSerializer, AModelSerializer)

    def test_dynamic_serializer_class_name(self):
        """Тест имени созданного класса"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()

            class Meta:
                model = User
                fields = ("field1",)

        # Создаем динамический сериализатор
        DynamicTestSerializer = dynamic_serializer(base_serializer=BaseTestSerializer, include_fields=("field1",))

        # Проверяем имя класса
        assert DynamicTestSerializer.__name__ == "DynamicSerializer"


@pytest.mark.skipif(DRF_AVAILABLE, reason="Skip when DRF is available")
class TestWithoutDRF:
    """Тесты когда Django REST Framework недоступен"""

    def test_import_without_drf(self):
        """Тест импорта модуля без DRF"""
        # Модуль должен импортироваться даже без DRF
        from adjango.serializers import dynamic_serializer

        assert dynamic_serializer is not None
