# managers/polymorphic.py
try:
    from polymorphic.managers import PolymorphicManager
    from adjango.managers.base import AManager


    class APolymorphicManager(PolymorphicManager, AManager):
        """
        Custom manager that combines async methods from AManager with polymorphic capabilities.
        Inherits from both PolymorphicManager and AManager to ensure all functionalities are available.
        """
        pass
except ImportError:
    pass
