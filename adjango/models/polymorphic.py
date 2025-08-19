# models/polymorphic.py
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from adjango.services.base import ABaseService

try:
    from asgiref.sync import sync_to_async
    from polymorphic.models import PolymorphicModel

    from adjango.managers.polymorphic import APolymorphicManager
    from adjango.models.base import AModel

    Self = TypeVar("Self", bound="APolymorphicModel")

    class APolymorphicModel(PolymorphicModel, AModel):
        """Enhanced polymorphic model with service integration."""

        objects: APolymorphicManager[Self]  # type: ignore

        class Meta:
            abstract = True

        async def aget_real_instance(self) -> "PolymorphicModel":
            """
            Async gets real instance of polymorphic model.

            :return: Real model instance or None if not found.
            """
            return await sync_to_async(self.get_real_instance)()

        @property
        def service(self) -> "ABaseService":
            """Return service instance for this model. Must be implemented in subclasses."""
            raise NotImplementedError(
                f"Define service property in your model {self.__class__.__name__}"
            )

except ImportError:
    # django-polymorphic not installed
    pass
