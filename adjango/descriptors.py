# descriptors.py
from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, cast

from django.db.models.fields.related_descriptors import ManyToManyDescriptor

from adjango.managers.base import AManager

if TYPE_CHECKING:
    from django.db.models import Model
    from adjango.querysets.base import AQuerySet

# Type variable for related model
_RM = TypeVar("_RM", bound="Model")


class AManyRelatedManager(AManager[_RM], Generic[_RM]):
    """Typed base manager for many-to-many relations.

    This class exists purely for static type checking.  The actual manager
    returned at runtime will subclass Django's dynamically generated
    ``ManyRelatedManager`` *and* this base class, giving access to the real
    implementation while preserving the generic ``_RM`` type information.
    """

    def all(self) -> "AQuerySet[_RM]": ...  # pragma: no cover - typing only

    async def aall(self) -> list[_RM]: ...  # pragma: no cover - typing only


class AManyToManyDescriptor(ManyToManyDescriptor, Generic[_RM]):
    def __get__(
        self, instance: "Model | None", owner: type | None = None
    ) -> AManyRelatedManager[_RM]:  # type: ignore[override]
        # ``ManyToManyDescriptor`` returns a dynamically created manager.  Casting
        # here preserves the concrete related model type for static analysers.
        return cast(AManyRelatedManager[_RM], super().__get__(instance, owner))

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
        class _AManyRelatedManager(
            original_manager_cls, AManyRelatedManager[related_model]  # type: ignore[type-arg]
        ):
            def all(self) -> "AQuerySet[related_model]":  # type: ignore[override]
                from adjango.querysets.base import AQuerySet

                # ``ManyRelatedManager`` returns a plain ``QuerySet``.  Casting
                # to ``AQuerySet`` preserves the async methods and typing.
                return cast(AQuerySet[related_model], super().all())

            async def aall(self) -> list[related_model]:  # type: ignore[valid-type]
                """Возвращает все связанные объекты."""
                from asgiref.sync import sync_to_async

                return await sync_to_async(list)(self.get_queryset())

        return _AManyRelatedManager

    def __set_name__(self, owner, name):
        """Вызывается когда дескриптор присваивается к атрибуту класса."""
        super().__set_name__(owner, name)
        self.name = name
