# descriptors.py
from django.db.models.fields.related_descriptors import ManyToManyDescriptor

from adjango.managers.base import AManager


class AManyToManyDescriptor(ManyToManyDescriptor):
    @property
    def related_manager_cls(self):
        # Get the original related_manager_cls
        original_manager_cls = super().related_manager_cls

        # Define a new manager class that extends the original and adds the 'aall' method
        class AManyRelatedManager(original_manager_cls, AManager):
            pass

        return AManyRelatedManager
