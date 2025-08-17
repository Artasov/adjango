# models/polymorphic.py

try:
    from adjango.services.object.polymorphic import APolymorphicModelObjectBaseService
    from polymorphic.models import PolymorphicModel
    from adjango.managers.polymorphic import APolymorphicManager


    class APolymorphicModel(PolymorphicModel, APolymorphicModelObjectBaseService):
        objects = APolymorphicManager()

        class Meta:
            abstract = True
except ImportError:
    pass
