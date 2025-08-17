# models/base.py
from django.contrib.auth.models import AbstractUser
from django.db.models import Model

from adjango.managers.base import AManager, AUserManager
from adjango.services.base import ABaseService
from adjango.services.object.base import ABaseModelObjectService


class AModel(Model, ABaseModelObjectService[ABaseService]):
    objects = AManager()

    class Meta:
        abstract = True


class AAbstractUser(AbstractUser, AModel):
    objects = AUserManager()

    class Meta:
        abstract = True
