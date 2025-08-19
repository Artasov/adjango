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


# Simple test model to avoid issues with User
class TestModel(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    class Meta:
        app_label = "test_app"


@pytest.mark.skipif(not DRF_AVAILABLE, reason="Django REST Framework not available")
class TestDynamicSerializer:
    """Tests for dynamic_serializer function"""

    def test_dynamic_serializer_basic(self):
        """Test basic dynamic_serializer functionality"""

        # Create base serializer
        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()
            field2 = IntegerField()
            field3 = CharField()

            class Meta:
                model = User
                fields = ("field1", "field2", "field3")

        # Create dynamic serializer with limited fields
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer, include_fields=("field1", "field2")
        )

        # Check that new serializer is created
        assert DynamicTestSerializer is not None
        assert issubclass(DynamicTestSerializer, BaseTestSerializer)

        # Check Meta class
        assert hasattr(DynamicTestSerializer, "Meta")
        assert DynamicTestSerializer.Meta.fields == ("field1", "field2")

    def test_dynamic_serializer_with_field_overrides_class(self):
        """Test dynamic_serializer with field overrides through class"""

        class BaseTestSerializer(AModelSerializer):
            class Meta:
                model = User
                fields = ("username", "email")

        class CustomFieldSerializer(BaseSerializer):
            pass

        # Create dynamic serializer with field override
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer,
            include_fields=("username", "email"),
            field_overrides={"username": CustomFieldSerializer},
        )

        # Check that field is overridden
        instance = DynamicTestSerializer()
        assert "username" in instance.fields
        assert isinstance(instance.fields["username"], CustomFieldSerializer)
        assert instance.fields["username"].read_only is True

    def test_dynamic_serializer_with_field_overrides_instance(self):
        """Test dynamic_serializer with field overrides through instance"""

        class BaseTestSerializer(AModelSerializer):
            class Meta:
                model = User
                fields = ("username", "email")

        class CustomFieldSerializer(BaseSerializer):
            pass

        custom_instance = CustomFieldSerializer(read_only=False)

        # Create dynamic serializer with field override
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer,
            include_fields=("username", "email"),
            field_overrides={"email": custom_instance},
        )

        # Check that field is overridden
        instance = DynamicTestSerializer()
        assert "email" in instance.fields
        assert instance.fields["email"] is custom_instance
        assert instance.fields["email"].read_only is False

    def test_dynamic_serializer_invalid_field_override(self):
        """Test dynamic_serializer with invalid field override"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()

            class Meta:
                model = User
                fields = ("field1",)

        # Attempt to override field with invalid value
        with pytest.raises(ValueError, match="Invalid serializer for field 'field1'"):
            dynamic_serializer(
                base_serializer=BaseTestSerializer,
                include_fields=("field1",),
                field_overrides={"field1": "invalid_serializer"},
            )

    def test_dynamic_serializer_no_field_overrides(self):
        """Test dynamic_serializer without field overrides"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()
            field2 = IntegerField()
            field3 = CharField()

            class Meta:
                model = User
                fields = ("field1", "field2", "field3")

        # Create dynamic serializer without overrides
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer, include_fields=("field1", "field3")
        )

        # Check that serializer is created correctly
        assert DynamicTestSerializer is not None
        assert DynamicTestSerializer.Meta.fields == ("field1", "field3")

        # Check that we can create instance
        instance = DynamicTestSerializer()
        assert instance is not None

    def test_dynamic_serializer_empty_include_fields(self):
        """Test dynamic_serializer with empty field list"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()

            class Meta:
                model = User
                fields = ("field1",)

        # Create dynamic serializer with empty fields
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer, include_fields=()
        )

        assert DynamicTestSerializer.Meta.fields == ()

    def test_dynamic_serializer_inheritance(self):
        """Test inheritance from base serializer"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()

            class Meta:
                model = User
                fields = ("field1",)

            def custom_method(self):
                return "base_method"

        # Create dynamic serializer
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer, include_fields=("field1",)
        )

        # Check method inheritance
        instance = DynamicTestSerializer()
        assert hasattr(instance, "custom_method")
        assert instance.custom_method() == "base_method"

    def test_dynamic_serializer_meta_inheritance(self):
        """Test Meta class inheritance"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()

            class Meta:
                model = User
                fields = ("field1",)
                read_only_fields = ("field1",)
                extra_kwargs = {"field1": {"required": False}}

        # Create dynamic serializer
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer, include_fields=("field1",)
        )

        # Check Meta attributes inheritance
        assert hasattr(DynamicTestSerializer.Meta, "read_only_fields")
        assert hasattr(DynamicTestSerializer.Meta, "extra_kwargs")
        assert DynamicTestSerializer.Meta.read_only_fields == ("field1",)

    def test_dynamic_serializer_multiple_field_overrides(self):
        """Test dynamic_serializer with multiple field overrides"""

        class BaseTestSerializer(AModelSerializer):
            class Meta:
                model = User
                fields = ("username", "email", "first_name")

        class CustomSerializer1(BaseSerializer):
            pass

        class CustomSerializer2(BaseSerializer):
            pass

        custom_instance = CustomSerializer2()

        # Create dynamic serializer with multiple overrides
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer,
            include_fields=("username", "email", "first_name"),
            field_overrides={
                "username": CustomSerializer1,
                "first_name": custom_instance,
            },
        )

        # Check overrides
        instance = DynamicTestSerializer()
        assert isinstance(instance.fields["username"], CustomSerializer1)
        assert instance.fields["first_name"] is custom_instance
        # email should remain original - it's EmailField from User model
        assert "email" in instance.fields

    def test_dynamic_serializer_return_type(self):
        """Test return type"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()

            class Meta:
                model = User
                fields = ("field1",)

        # Create dynamic serializer
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer, include_fields=("field1",)
        )

        # Check that class is returned
        assert isinstance(DynamicTestSerializer, type)
        assert issubclass(DynamicTestSerializer, BaseTestSerializer)
        assert issubclass(DynamicTestSerializer, AModelSerializer)

    def test_dynamic_serializer_class_name(self):
        """Test created class name"""

        class BaseTestSerializer(AModelSerializer):
            field1 = CharField()

            class Meta:
                model = User
                fields = ("field1",)

        # Create dynamic serializer
        DynamicTestSerializer = dynamic_serializer(
            base_serializer=BaseTestSerializer, include_fields=("field1",)
        )

        # Check class name
        assert DynamicTestSerializer.__name__ == "DynamicSerializer"


@pytest.mark.skipif(DRF_AVAILABLE, reason="Skip when DRF is available")
class TestWithoutDRF:
    """Tests when Django REST Framework is unavailable"""

    def test_import_without_drf(self):
        """Test module import without DRF"""
        # Module should import even without DRF
        from adjango.serializers import dynamic_serializer

        assert dynamic_serializer is not None
