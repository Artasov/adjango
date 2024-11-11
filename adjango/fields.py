# fields.py
from django.db.models import ManyToManyField

from adjango.descriptors import AManyToManyDescriptor


class AManyToManyField(ManyToManyField):
    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        # Replace the descriptor with our custom one
        setattr(cls, self.name, AManyToManyDescriptor(self.remote_field, reverse=False))
