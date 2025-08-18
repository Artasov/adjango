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

        # Determine the related model for proper typing of the manager.
        # Fallback to generic ``Model`` if it cannot be resolved (shouldn't happen
        # in normal Django usage but keeps the typing safe).
        related_model = self._related_model
        if related_model is None:
            from django.db.models import Model as _Model  # local import to avoid cycles

            related_model = _Model

        # Define a new manager class that extends the original and adds the
        # typed ``aall`` method.  Using ``related_model`` in the annotations
        # allows IDEs and type checkers to infer the concrete model type instead
        # of the generic ``_RM`` placeholder.
        class AManyRelatedManager(original_manager_cls, AManager[related_model]):  # type: ignore[type-arg]
            async def aall(self) -> list[related_model]:  # type: ignore[valid-type]
                """Возвращает все связанные объекты."""
                from asgiref.sync import sync_to_async

                return await sync_to_async(list)(self.get_queryset())

        return AManyRelatedManager

    def __set_name__(self, owner, name):
        """Вызывается когда дескриптор присваивается к атрибуту класса."""
        super().__set_name__(owner, name)
        self.name = name
