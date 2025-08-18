# managers/polymorphic.py
try:
    from polymorphic.managers import PolymorphicManager

    from adjango.querysets.polymorphic import APolymorphicQuerySet

    class APolymorphicManager(PolymorphicManager.from_queryset(APolymorphicQuerySet)):  # type: ignore
        pass

except ImportError:
    pass
