# managers/polymorphic.py
from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from django.db.models import Model

try:
    from polymorphic.managers import PolymorphicManager

    from adjango.querysets.polymorphic import APolymorphicQuerySet

    # Type variable for generic polymorphic manager
    _M = TypeVar("_M", bound="Model")

    class APolymorphicManager(PolymorphicManager.from_queryset(APolymorphicQuerySet), Generic[_M]):  # type: ignore
        """Enhanced polymorphic manager with proper type hints."""

        pass

except ImportError:
    pass
