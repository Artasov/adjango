from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from adjango.models.base import AModel

ModelT = TypeVar("ModelT", bound="AModel[Any]")


class ABaseService(Generic[ModelT], ABC):
    """Base service class for model operations."""

    def __init__(self, obj: ModelT) -> None:
        """Initialize service with model instance."""
        self.obj: ModelT = obj
