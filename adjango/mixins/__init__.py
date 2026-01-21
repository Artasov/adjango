# Polymorphic mixins are optional and require django-polymorphic
try:
    from .polymorphic import PolymorphicTypeAdminMixin
    __all__ = ['PolymorphicTypeAdminMixin']
except ImportError:
    __all__ = []
