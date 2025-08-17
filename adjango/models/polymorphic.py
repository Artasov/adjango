# models/polymorphic.py
from typing import TypeVar, Generic

from adjango.services.base import ABaseService

try:
    from adjango.services.object.polymorphic import APolymorphicModelObjectBaseService
    from polymorphic.models import PolymorphicModel
    from adjango.managers.polymorphic import APolymorphicManager

    ServiceT = TypeVar('ServiceT', bound=ABaseService)


    class APolymorphicModel(PolymorphicModel, APolymorphicModelObjectBaseService[ServiceT], Generic[ServiceT]):
        objects = APolymorphicManager()

        class Meta:
            abstract = True
except ImportError:
    pass
