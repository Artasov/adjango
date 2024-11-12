# models/polymorphic.py

try:
    from adjango.services.polymorphic import APolymorphicBaseService
    from polymorphic.models import PolymorphicModel
    from adjango.managers.polymorphic import APolymorphicManager


    class APolymorphicModel(PolymorphicModel, APolymorphicBaseService):
        objects = APolymorphicManager()

        class Meta:
            abstract = True
except ImportError:
    pass
