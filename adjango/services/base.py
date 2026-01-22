from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, Type, TypeVar, Union

if TYPE_CHECKING:
    from adjango.models.base import Model
    from django.db.models import Model as DjangoModel

    from django.db.models import QuerySet

_M = TypeVar("_M", bound="DjangoModel")


class BaseService(ABC):
    """Base service class for model operations."""

    def __init__(self, obj: Union["Model", "DjangoModel"]) -> None:
        """Initialize service with model instance."""
        self.obj: Union["Model", "DjangoModel"] = obj

    @staticmethod
    def getorn(
        queryset: "QuerySet[_M]",
        exception: Type[Exception] | Exception | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> _M | None:
        """
        Gets single object from given QuerySet matching passed parameters.

        :param queryset: QuerySet to get object from.
        :param exception: Exception class or exception instance to raise if object not found.
                          If None, returns None.

        :return: Model object or None if object not found and exception not specified.
        """
        try:
            return queryset.get(*args, **kwargs)
        except queryset.model.DoesNotExist:
            if exception is not None:
                if isinstance(exception, type):
                    raise exception()
                else:
                    raise exception
        return None

    @staticmethod
    async def agetorn(
        queryset: "QuerySet[_M]",
        exception: Type[Exception] | Exception | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> _M | None:
        """
        Async gets single object from given QuerySet matching passed parameters.

        :param queryset: QuerySet to get object from.
        :param exception: Exception class or exception instance to raise if object not found.
                          If None, returns None.

        :return: Model object or None if object not found and exception not specified.
        """
        try:
            return await queryset.aget(*args, **kwargs)
        except queryset.model.DoesNotExist:
            if exception is not None:
                if isinstance(exception, type):
                    raise exception()
                else:
                    raise exception
        return None
