# models/polymorphic.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from adjango.services.base import ABaseService

try:
    from polymorphic.models import PolymorphicModel

    from adjango.managers.polymorphic import APolymorphicManager
    from adjango.services.object.polymorphic import APolymorphicModelObjectBaseService

    ServiceT = TypeVar("ServiceT", bound="ABaseService[Any]")

    class APolymorphicModel(
        PolymorphicModel,
        APolymorphicModelObjectBaseService[ServiceT],
        Generic[ServiceT],
    ):
        """Enhanced polymorphic model with service integration."""

        objects = APolymorphicManager()

        class Meta:
            abstract = True

except ImportError:
    # django-polymorphic not installed
    pass
