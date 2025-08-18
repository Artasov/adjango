# descriptors.py
from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from django.db.models.fields.related_descriptors import ManyToManyDescriptor

from adjango.managers.base import AManager

if TYPE_CHECKING:
    from django.db.models import Model

# Type variable for related model
_RM = TypeVar("_RM", bound="Model")


class AManyToManyDescriptor(ManyToManyDescriptor, Generic[_RM]):
    def __init__(self, rel, reverse=False):
        super().__init__(rel, reverse)
        self._related_model = None
        if hasattr(rel, "related_model"):
            self._related_model = rel.related_model
        elif hasattr(rel, "model"):
            self._related_model = rel.model

    @property
    def related_manager_cls(self):
        # Get the original related_manager_cls
        original_manager_cls = super().related_manager_cls

        # Define a new manager class that extends the original and adds the 'aall' method
        class AManyRelatedManager(original_manager_cls, AManager[_RM]):
            async def aall(self) -> list[_RM]:
                """Возвращает все связанные объекты."""
                from asgiref.sync import sync_to_async

                return await sync_to_async(list)(self.get_queryset())

        return AManyRelatedManager

    def __set_name__(self, owner, name):
        """Вызывается когда дескриптор присваивается к атрибуту класса."""
        super().__set_name__(owner, name)
        self.name = name
