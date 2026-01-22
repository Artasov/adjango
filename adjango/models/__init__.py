from .base import Model

try:
    from .polymorphic import PolymorphicModel
except ImportError:
    pass
