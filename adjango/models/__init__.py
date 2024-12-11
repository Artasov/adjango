from .base import AModel

try:
    from .polymorphic import APolymorphicModel
except ImportError:
    pass
