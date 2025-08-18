# serializers.py
try:
    from rest_framework import status
    from rest_framework.exceptions import APIException
    from rest_framework.serializers import BaseSerializer  # noqa
    from rest_framework.serializers import ListSerializer as DRFListSerializer
    from rest_framework.serializers import ModelSerializer as DRFModelSerializer
    from rest_framework.serializers import Serializer as DRFSerializer
    from rest_framework.status import HTTP_400_BAD_REQUEST
except ImportError:
    pass
from typing import Dict, Optional, Tuple, Type, TypeVar, Union, cast

from adjango.aserializers import AModelSerializer

T = TypeVar("T", bound=AModelSerializer)


def dynamic_serializer(
    base_serializer: Type[T],
    include_fields: Tuple[str, ...],
    field_overrides: Optional[
        Dict[str, Union[Type[BaseSerializer], BaseSerializer]]
    ] = None,
) -> Type[T]:
    """
    Creates dynamic serializer based on base serializer,
    including specified fields and overriding some of them when needed.

    :param base_serializer: Base serializer class.
    :param include_fields: Tuple of field names to include.
    :param field_overrides: Dictionary with field overrides, where key is field name,
                            and value is serializer class or serializer instance.
    :return: New serializer class.
    """

    # Create new Meta class with needed fields
    class Meta(base_serializer.Meta):
        fields = include_fields

    # Attributes dictionary for new serializer
    attrs = {"Meta": Meta}

    # If there are field overrides, add them
    if field_overrides:
        for field_name, serializer in field_overrides.items():
            if isinstance(serializer, type) and issubclass(serializer, BaseSerializer):
                # If serializer class is passed, create its instance
                # Assume that if field is related to multiple objects, many=True should be specified
                # Here we can add logic to determine many=True based on model or other conditions
                # For simplicity assume it's not required
                attrs[field_name] = serializer(read_only=True)
            elif isinstance(serializer, BaseSerializer):
                # If serializer instance is passed, use it directly
                attrs[field_name] = serializer
            else:
                raise ValueError(f"Invalid serializer for field '{field_name}'.")

    # Create new serializer class
    dynamic_class = type("DynamicSerializer", (base_serializer,), attrs)

    # Cast type to Type[T] using cast
    return cast(Type[T], dynamic_class)
