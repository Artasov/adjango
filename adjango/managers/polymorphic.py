# managers/polymorphic.py
try:
    from polymorphic.managers import PolymorphicManager
    from adjango.querysets.polymorphic import APolymorphicQuerySet

    class APolymorphicManager(PolymorphicManager.from_queryset(APolymorphicQuerySet)):
        pass

except ImportError:
    pass
