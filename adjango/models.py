from django.db.models import Model

from adjango.managers.base import AManager
from adjango.services.base import ABaseService


class AModel(Model, ABaseService):
    objects = AManager()

    class Meta:
        abstract = True
