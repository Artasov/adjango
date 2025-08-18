from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adjango.models.base import AModel


class ABaseService(ABC):
    """Base service class for model operations."""

    def __init__(self, obj: "AModel") -> None:
        """Initialize service with model instance."""
        self.obj: "AModel" = obj
