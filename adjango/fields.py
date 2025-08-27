from __future__ import annotations

from typing import Any, Generic, TypeVar, cast, overload

from django.db.models import ManyToManyField, Model

from adjango.descriptors import AManyToManyDescriptor
from adjango.managers.base import AManager

_M = TypeVar('_M', bound=Model)


class AManyToManyField(ManyToManyField, Generic[_M]):
    @overload
    def __get__(self, instance: None, owner: type[Any]) -> "AManyToManyField[_M]":
        ...

    @overload
    def __get__(self, instance: Any, owner: type[Any]) -> AManager[_M]:
        ...

    def __get__(self, instance: Any, owner: type[Any]) -> AManager[_M]:
        return cast(AManager[_M], super().__get__(instance, owner))  # type: ignore[misc]

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, AManyToManyDescriptor(self.remote_field, reverse=False))
