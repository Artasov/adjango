# serializers.py
try:
    from rest_framework.serializers import (
        ListSerializer as DRFListSerializer,
        ModelSerializer as DRFModelSerializer,
        Serializer as DRFSerializer,
        BaseSerializer,
    )
    from rest_framework import status
    from rest_framework.exceptions import APIException
    from rest_framework.status import HTTP_400_BAD_REQUEST
except ImportError:
    pass
from typing import Type, Optional, Dict, Tuple, cast, Union, TypeVar

from adjango.aserializers import AModelSerializer

T = TypeVar('T', bound=AModelSerializer)


def create_dynamic_serializer(
        base_serializer: Type[T],
        include_fields: Tuple[str, ...],
        field_overrides: Optional[Dict[str, Union[Type[BaseSerializer], BaseSerializer]]] = None
) -> Type[T]:
    """
    Создаёт динамический сериализатор на основе базового сериализатора,
    включая указанные поля и переопределяя некоторые из них при необходимости.

    :param base_serializer: Базовый класс сериализатора.
    :param include_fields: Кортеж имен полей для включения.
    :param field_overrides: Словарь с переопределениями полей, где ключ — имя поля,
                            а значение — класс сериализатора или экземпляр сериализатора.
    :return: Новый класс сериализатора.
    """

    # Создаём новый класс Meta с нужными полями
    class Meta(base_serializer.Meta):
        fields = include_fields

    # Словарь атрибутов для нового сериализатора
    attrs = {'Meta': Meta}

    # Если есть переопределения полей, добавляем их
    if field_overrides:
        for field_name, serializer in field_overrides.items():
            if isinstance(serializer, type) and issubclass(serializer, BaseSerializer):
                # Если передан класс сериализатора, создаём его экземпляр
                # Предполагаем, что если поле связано с множеством объектов, необходимо указать many=True
                # Здесь можно добавить логику определения many=True на основе модели или других условий
                # Для простоты предполагаем, что это не требуется
                attrs[field_name] = serializer(read_only=True)
            elif isinstance(serializer, BaseSerializer):
                # Если передан экземпляр сериализатора, используем его напрямую
                attrs[field_name] = serializer
            else:
                raise ValueError(f"Invalid serializer for field '{field_name}'.")

    # Создаём новый класс сериализатора
    dynamic_class = type('DynamicSerializer', (base_serializer,), attrs)

    # Приводим тип к Type[T] с помощью cast
    return cast(Type[T], dynamic_class)
