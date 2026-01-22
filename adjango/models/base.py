# models/base.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db.models import Model as DjangoModel

from adjango.utils.funcs import arelated

if TYPE_CHECKING:
    from adjango.services.base import BaseService


class Model(DjangoModel):
    """Base model class with enhanced functionality."""

    class Meta:
        abstract = True

    async def arelated(self, field: str) -> Any:
        """
        Get related field value asynchronously.
        """
        return await arelated(self, field)

    @property
    def service(self) -> 'BaseService':
        """Return service instance for this model. Must be implemented in subclasses."""
        raise NotImplementedError(f'Define service property in your model {self.__class__.__name__}')
