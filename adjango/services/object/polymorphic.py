# services/object/polymorphic.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from adjango.services.base import ABaseService

try:
    from asgiref.sync import sync_to_async
    from polymorphic.models import PolymorphicModel

    from adjango.services.object.base import ABaseModelObjectService

    ServiceT = TypeVar("ServiceT", bound="ABaseService[Any]")

    class APolymorphicModelObjectBaseService(
        ABaseModelObjectService[ServiceT], Generic[ServiceT]
    ):
        """Polymorphic model object service with async capabilities."""

        async def aget_real_instance(self: PolymorphicModel) -> PolymorphicModel:
            """
            Async gets real instance of polymorphic model.

            :return: Real model instance or None if not found.
            """
            return await sync_to_async(self.get_real_instance)()

except ImportError:
    # django-polymorphic not installed
    pass
