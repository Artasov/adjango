# models/base.py
from typing import Generic, TypeVar

from django.contrib.auth.models import AbstractUser
from django.db.models import Model

from adjango.managers.base import AManager, AUserManager
from adjango.services.base import ABaseService
from adjango.services.object.base import ABaseModelObjectService

ServiceT = TypeVar('ServiceT', bound=ABaseService)


class AModel(Model, ABaseModelObjectService[ServiceT], Generic[ServiceT]):
    objects = AManager()

    class Meta:
        abstract = True


class AAbstractUser(AbstractUser, AModel[ServiceT], Generic[ServiceT]):
    objects = AUserManager()

    class Meta:
        abstract = True
