from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from adjango.models.base import AModel
    from django.db.models import Model


class ABaseService(ABC):
    """Base service class for model operations."""

    def __init__(self, obj: Union['AModel', 'Model']) -> None:
        """Initialize service with model instance."""
        self.obj: Union['AModel', 'Model'] = obj
