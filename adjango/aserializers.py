# aserializers.py
from typing import List, Optional, TypedDict

try:
    from rest_framework import status
    from rest_framework.exceptions import APIException
    from rest_framework.serializers import (
        LIST_SERIALIZER_KWARGS,
        LIST_SERIALIZER_KWARGS_REMOVE,
    )
    from rest_framework.serializers import ListSerializer as DRFListSerializer
    from rest_framework.serializers import ModelSerializer as DRFModelSerializer
    from rest_framework.serializers import Serializer as DRFSerializer
    from rest_framework.status import HTTP_400_BAD_REQUEST
except ImportError:
    pass
from asgiref.sync import sync_to_async
from django.utils.translation import gettext_lazy as _


class FieldError(TypedDict):
    field: str
    message: str


def serializer_errors_to_field_errors(serializer_errors) -> List[FieldError]:
    field_errors = []
    for field, messages in serializer_errors.items():
        for message in messages:
            field_errors.append(FieldError(field=field, message=message))
    return field_errors


class DetailExceptionDict(TypedDict):
    message: str
    fields_errors: List[FieldError]


class DetailAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        detail: DetailExceptionDict,
        code: Optional[str] = None,
        status_code: Optional[str] = None,
    ):
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail=detail, code=code)
        if code is not None:
            self.default_code = code


class SerializerErrors(DetailAPIException):
    def __init__(
        self,
        serializer_errors: dict,
        code: Optional[str] = None,
        status_code: str = HTTP_400_BAD_REQUEST,
        message: str = _('Correct the mistakes.'),
    ):
        detail = DetailExceptionDict(
            message=message,
            fields_errors=serializer_errors_to_field_errors(serializer_errors),
        )
        super().__init__(detail=detail, code=code, status_code=status_code)


class AListSerializer(DRFListSerializer):
    @property
    async def adata(self):
        items_data = []
        for item in self.instance:
            # Create serializer for list item
            serializer = self.child.__class__(item, context=self.context)
            # Use sync_to_async to get data and avoid awaiting the same coroutine multiple times
            data = await sync_to_async(lambda: serializer.data)()
            items_data.append(data)
        return items_data


class ASerializer(DRFSerializer):
    async def asave(self, **kwargs):
        return await sync_to_async(self.save)(**kwargs)

    async def ais_valid(self, raise_exception=False, **kwargs):
        is_valid = await sync_to_async(self.is_valid)(**kwargs)
        if raise_exception and not is_valid:
            raise SerializerErrors(self.errors)
        return is_valid

    @property
    async def adata(self):
        return await sync_to_async(lambda: self.data)()

    @property
    async def avalid_data(self):
        return await sync_to_async(lambda: self.validated_data)()

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        return AListSerializer(*args, **kwargs)


class AModelSerializer(DRFModelSerializer):
    async def asave(self, **kwargs):
        return await sync_to_async(self.save)(**kwargs)

    async def ais_valid(self, raise_exception=False, **kwargs):
        is_valid = await sync_to_async(self.is_valid)(**kwargs)
        if raise_exception and not is_valid:
            raise SerializerErrors(self.errors)
        return is_valid

    def is_valid(self, raise_exception=False, **kwargs):
        is_valid = super().is_valid(**kwargs)
        if raise_exception and not is_valid:
            raise SerializerErrors(self.errors)
        return is_valid

    @property
    async def adata(self):
        return await sync_to_async(lambda: self.data)()

    @property
    async def avalid_data(self):
        return await sync_to_async(lambda: self.validated_data)()

    @classmethod
    def many_init(cls, *args, **kwargs):
        # Prepare arguments for ListSerializer and child serializer
        list_kwargs = {}

        # Parameters that should go to ListSerializer (e.g., allow_empty)
        list_serializer_kwargs = {key: value for key, value in kwargs.items() if key in LIST_SERIALIZER_KWARGS}

        # Parameters that should be removed from kwargs (e.g., many)
        for key in LIST_SERIALIZER_KWARGS_REMOVE:
            kwargs.pop(key, None)

        # Extract data that should be passed to ListSerializer, not to child
        data = kwargs.pop('data', None)

        # Arguments for child without list-specific parameters and without data
        child_kwargs = {key: value for key, value in kwargs.items() if key not in LIST_SERIALIZER_KWARGS}

        # Create child
        list_kwargs['child'] = cls(*args, **child_kwargs)

        # Add back list-specific parameters
        list_kwargs.update(list_serializer_kwargs)

        # Pass data to ListSerializer
        if data is not None:
            list_kwargs['data'] = data

        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(meta, 'list_serializer_class', AListSerializer)
        return list_serializer_class(*args, **list_kwargs)
