from typing import Any, cast, TypeVar, Generic

from django.db.models.fields.related_descriptors import ManyToManyDescriptor
from django.utils.functional import cached_property

from adjango.managers.base import AManager

_M = TypeVar("_M")


class AManyToManyDescriptor(ManyToManyDescriptor, Generic[_M]):
    @cached_property
    def related_manager_cls(self):
        base_cls = super().related_manager_cls
        return type("AManyRelatedManager", (base_cls, AManager), {})

    def __get__(self, instance: Any, cls: type | None = None) -> AManager[_M]:
        return cast(AManager[_M], super().__get__(instance, cls))
