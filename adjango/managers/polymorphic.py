# managers/polymorphic.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Iterable, TypeVar, cast

if TYPE_CHECKING:
    from django.db.models import Model

try:
    from polymorphic.managers import PolymorphicManager

    from adjango.querysets.polymorphic import APolymorphicQuerySet

    # Type variable for generic polymorphic manager
    _M = TypeVar("_M", bound="Model")

    class APolymorphicManager(PolymorphicManager.from_queryset(APolymorphicQuerySet), Generic[_M]):  # type: ignore
        """Enhanced polymorphic manager with proper type hints."""

        def get_queryset(self) -> APolymorphicQuerySet[_M]:  # type: ignore[override]
            return cast(APolymorphicQuerySet[_M], super().get_queryset())

        async def aall(self) -> list[_M]:
            return await self.get_queryset().aall()

        async def afilter(self, *args: Any, **kwargs: Any) -> list[_M]:
            return await self.get_queryset().afilter(*args, **kwargs)

        async def aget(self, *args: Any, **kwargs: Any) -> _M:
            return await self.get_queryset().aget(*args, **kwargs)

        async def afirst(self) -> _M | None:
            return await self.get_queryset().afirst()

        async def alast(self) -> _M | None:
            return await self.get_queryset().alast()

        async def acreate(self, **kwargs: Any) -> _M:
            return await self.get_queryset().acreate(**kwargs)

        async def aget_or_create(self, defaults=None, **kwargs: Any) -> tuple[_M, bool]:
            return await self.get_queryset().aget_or_create(defaults=defaults, **kwargs)

        async def aupdate_or_create(self, defaults=None, **kwargs: Any) -> tuple[_M, bool]:
            return await self.get_queryset().aupdate_or_create(defaults=defaults, **kwargs)

        async def acount(self) -> int:
            return await self.get_queryset().acount()

        async def aexists(self) -> bool:
            return await self.get_queryset().aexists()

        async def aset(self, data: Iterable[_M], *args: Any, **kwargs: Any) -> None:
            await self.get_queryset().aset(data, *args, **kwargs)

        async def aadd(self, data: _M, *args: Any, **kwargs: Any) -> None:
            await self.get_queryset().aadd(data, *args, **kwargs)

        def filter(self, *args: Any, **kwargs: Any) -> APolymorphicQuerySet[_M]:  # type: ignore[override]
            return cast(APolymorphicQuerySet[_M], super().filter(*args, **kwargs))

        def exclude(self, *args: Any, **kwargs: Any) -> APolymorphicQuerySet[_M]:  # type: ignore[override]
            return cast(APolymorphicQuerySet[_M], super().exclude(*args, **kwargs))

        def prefetch_related(self, *lookups: Any) -> APolymorphicQuerySet[_M]:  # type: ignore[override]
            return cast(APolymorphicQuerySet[_M], super().prefetch_related(*lookups))

        def select_related(self, *fields: Any) -> APolymorphicQuerySet[_M]:  # type: ignore[override]
            return cast(APolymorphicQuerySet[_M], super().select_related(*fields))

except ImportError:
    pass
