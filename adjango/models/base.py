# models/base.py
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar, cast

from django.contrib.auth.models import AbstractUser
from django.db.models import Model

from adjango.managers.base import AManager, AUserManager
from adjango.utils.funcs import arelated

if TYPE_CHECKING:
    from adjango.services.base import ABaseService

Self = TypeVar("Self", bound="AModel")


class AModel(Model):
    """Base model class with enhanced functionality."""

    objects: AManager[Self]  # type: ignore

    class Meta:
        abstract = True

    async def arelated(self, field: str) -> Any:
        """
        Get related field value asynchronously.

        Для лучшей типизации используйте прямые обращения к полям:
        - order.user для ForeignKey
        - await order.products.aall() для ManyToMany
        """
        return await arelated(self, field)

    @property
    @abstractmethod
    def service(self) -> "ABaseService":
        """Return service instance for this model. Must be implemented in subclasses."""
        raise NotImplementedError(f"Define service property in your model {self.__class__.__name__}")


class AAbstractUser(AbstractUser, AModel):
    """Enhanced abstract user model with service integration."""

    objects: AUserManager[Self]  # type: ignore

    class Meta:
        abstract = True
