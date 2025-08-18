# managers/base.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Iterable, TypeVar, cast

from asgiref.sync import sync_to_async
from django.contrib.auth.models import UserManager
from django.db.models import Manager

from adjango.querysets.base import AQuerySet

if TYPE_CHECKING:
    from django.db.models import Model

# Type variable for generic Manager
_M = TypeVar("_M", bound="Model")


class AManager(Manager.from_queryset(AQuerySet), Generic[_M]):  # type: ignore
    """Асинхронный менеджер с типизированными методами."""

    def get_queryset(self) -> AQuerySet[_M]:  # type: ignore[override]
        return cast(AQuerySet[_M], super().get_queryset())

    async def aall(self) -> list[_M]:
        return await self.get_queryset().aall()

    async def afilter(self, *args, **kwargs) -> list[_M]:
        return await self.get_queryset().afilter(*args, **kwargs)

    async def aget(self, *args, **kwargs) -> _M:
        return await self.get_queryset().aget(*args, **kwargs)

    async def afirst(self) -> _M | None:
        return await self.get_queryset().afirst()

    async def alast(self) -> _M | None:
        return await self.get_queryset().alast()

    async def acreate(self, **kwargs) -> _M:
        return await self.get_queryset().acreate(**kwargs)

    async def aget_or_create(self, defaults=None, **kwargs) -> tuple[_M, bool]:
        return await self.get_queryset().aget_or_create(defaults=defaults, **kwargs)

    async def aupdate_or_create(self, defaults=None, **kwargs) -> tuple[_M, bool]:
        return await self.get_queryset().aupdate_or_create(defaults=defaults, **kwargs)

    async def acount(self) -> int:
        return await self.get_queryset().acount()

    async def aexists(self) -> bool:
        return await self.get_queryset().aexists()

    async def aset(self, data: Iterable[_M], *args: Any, **kwargs: Any) -> None:
        """Асинхронная версия set() для ManyToMany полей."""
        await self.get_queryset().aset(data, *args, **kwargs)

    async def aadd(self, data: _M, *args: Any, **kwargs: Any) -> None:
        """Асинхронная версия add() для ManyToMany полей."""
        await self.get_queryset().aadd(data, *args, **kwargs)

    # Typed queryset-returning methods to preserve chaining types
    def filter(self, *args: Any, **kwargs: Any) -> AQuerySet[_M]:  # type: ignore[override]
        return cast(AQuerySet[_M], super().filter(*args, **kwargs))

    def exclude(self, *args: Any, **kwargs: Any) -> AQuerySet[_M]:  # type: ignore[override]
        return cast(AQuerySet[_M], super().exclude(*args, **kwargs))

    def prefetch_related(self, *lookups: Any) -> AQuerySet[_M]:  # type: ignore[override]
        return cast(AQuerySet[_M], super().prefetch_related(*lookups))

    def select_related(self, *fields: Any) -> AQuerySet[_M]:  # type: ignore[override]
        return cast(AQuerySet[_M], super().select_related(*fields))


class AUserManager(UserManager, AManager[_M]):
    async def acreate_user(self, **extra_fields) -> _M:
        return await sync_to_async(self.create_user)(**extra_fields)
