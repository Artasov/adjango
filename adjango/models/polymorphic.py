# models/polymorphic.py
from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Self

if TYPE_CHECKING:
    from adjango.services.base import ABaseService

try:
    from asgiref.sync import sync_to_async
    from polymorphic.models import PolymorphicModel

    from adjango.managers.polymorphic import APolymorphicManager
    from adjango.models.base import AModel


    class APolymorphicModel(PolymorphicModel, AModel):
        """Enhanced polymorphic model with service integration."""

        objects: APolymorphicManager[Self] = APolymorphicManager()

        class Meta:
            abstract = True

        async def aget_real_instance(self) -> Self | None:
            """
            Async gets real instance of polymorphic model.

            :return: Real model instance or None if not found.
            """
            return await sync_to_async(self.get_real_instance)()

        @property
        def service(self) -> "ABaseService":
            """Return service instance for this model. Must be implemented in subclasses."""
            raise NotImplementedError(f"Define service property in your model {self.__class__.__name__}")

except ImportError:
    # django-polymorphic not installed
    pass
