# models/polymorphic.py
try:
    from polymorphic.models import PolymorphicModel
    from adjango.managers.polymorphic import APolymorphicManager
    from adjango.services.base import ABaseService


    class APolymorphicModel(PolymorphicModel, ABaseService):
        objects = APolymorphicManager()

        class Meta:
            abstract = True
except ImportError:
    pass
