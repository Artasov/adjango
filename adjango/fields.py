# fields.py
from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from django.db.models import ManyToManyField

from adjango.descriptors import AManyToManyDescriptor

if TYPE_CHECKING:
    from django.db.models import Model
    from adjango.managers.base import AManager

_RM = TypeVar("_RM", bound="Model")


class AManyToManyField(ManyToManyField):
    if TYPE_CHECKING:
        def __get__(self, instance: "Model | None", owner: type | None = None) -> AManager[_RM]: ...
    def __class_getitem__(cls, item):
        """Поддержка для Generic типизации AManyToManyField[Model]."""
        # Сохраняем информацию о типе для дальнейшего использования
        field_instance = cls.__new__(cls)
        field_instance._generic_type = item
        return field_instance

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        # Replace the descriptor with our custom one
        setattr(cls, self.name, AManyToManyDescriptor(self.remote_field, reverse=False))
