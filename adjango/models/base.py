# models/base.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from django.contrib.auth.models import AbstractUser
from django.db.models import Model

from adjango.managers.base import AManager, AUserManager
from adjango.services.object.base import ABaseModelObjectService

if TYPE_CHECKING:
    from adjango.services.base import ABaseService

ServiceT = TypeVar("ServiceT", bound="ABaseService[Any]")


class AModel(Model, ABaseModelObjectService[ServiceT], Generic[ServiceT]):
    """Base model class with enhanced functionality."""

    objects = AManager()

    class Meta:
        abstract = True


class AAbstractUser(AbstractUser, AModel[ServiceT], Generic[ServiceT]):
    """Enhanced abstract user model with service integration."""

    objects = AUserManager()

    class Meta:
        abstract = True
