# managers/base.py
from __future__ import annotations

from typing import Any, Generic, Iterable, TypeVar

from asgiref.sync import sync_to_async
from django.contrib.auth.models import UserManager
from django.db.models import Model

from adjango.querysets.base import AQuerySet

_M = TypeVar("_M", bound=Model)

from django.db.models import Manager as _ManagerBase


class AManager(_ManagerBase, Generic[_M]):
    """Asynchronous manager."""

    def get_queryset(self) -> Union[AQuerySet[_M], QuerySet[_M]]:
        return AQuerySet(self.model, using=self._db, hints=self._hints)

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
        await self.get_queryset().aset(data, *args, **kwargs)

    async def aadd(self, data: _M, *args: Any, **kwargs: Any) -> None:
        await self.get_queryset().aadd(data, *args, **kwargs)

    def all(self) -> Union[AQuerySet[_M], QuerySet[_M]]:
        return super().all()

    def filter(self, *args: Any, **kwargs: Any) -> Union[AQuerySet[_M], QuerySet[_M]]:
        return super().filter(*args, **kwargs)

    def exclude(self, *args: Any, **kwargs: Any) -> Union[AQuerySet[_M], QuerySet[_M]]:
        return super().exclude(*args, **kwargs)

    def prefetch_related(self, *lookups: Any) -> Union[AQuerySet[_M], QuerySet[_M]]:
        return super().prefetch_related(*lookups)

    def select_related(self, *fields: Any) -> Union[AQuerySet[_M], QuerySet[_M]]:
        return super().select_related(*fields)


class AUserManager(UserManager, AManager[_M]):
    async def acreate_user(self, **extra_fields) -> _M:
        return await sync_to_async(self.create_user)(**extra_fields)
