# models/base.py
from django.contrib.auth.models import AbstractUser
from django.db.models import Model

from adjango.managers.base import AManager, AUserManager
from adjango.services.base import ABaseService


class AModel(Model, ABaseService):
    objects = AManager()

    class Meta:
        abstract = True


class AAbstractUser(AbstractUser, AModel):
    objects = AUserManager()

    class Meta:
        abstract = True
