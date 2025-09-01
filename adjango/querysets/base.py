# querysets/base.py
from __future__ import annotations

from typing import Generic, Iterator, Type, TypeVar, Union, cast

from asgiref.sync import sync_to_async
from django.db.models import QuerySet

from adjango.utils.funcs import aadd, agetorn, aset, getorn

_M = TypeVar('_M', bound='Model')


class AQuerySet(QuerySet[_M], Generic[_M]):
    async def aall(self) -> list[_M]:
        return await self._aall_from_queryset(self)

    def getorn(self, exception: Type[Exception] | Exception | None = None, *args, **kwargs) -> _M | None:
        return getorn(self, exception, *args, **kwargs)

    async def agetorn(self, exception: Type[Exception] | Exception | None = None, *args, **kwargs) -> _M | None:
        return await agetorn(self, exception, *args, **kwargs)

    async def afilter(self, *args, **kwargs) -> list[_M]:
        filtered_qs = self.filter(*args, **kwargs)
        return await self._aall_from_queryset(filtered_qs)

    @staticmethod
    async def _aall_from_queryset(queryset) -> list[_M]:
        return await sync_to_async(list)(queryset)

    async def aset(self, data, *args, **kwargs) -> None:
        return await aset(self, data, *args, **kwargs)

    async def aadd(self, data, *args, **kwargs) -> None:
        return await aadd(self, data, *args, **kwargs)

    async def aget(self, *args, **kwargs) -> _M:
        return await sync_to_async(self.get)(*args, **kwargs)

    async def afirst(self) -> _M | None:
        return await sync_to_async(self.first)()

    async def alast(self) -> _M | None:
        return await sync_to_async(self.last)()

    async def acreate(self, **kwargs) -> _M:
        return await sync_to_async(self.create)(**kwargs)

    async def aget_or_create(self, defaults=None, **kwargs) -> tuple[_M, bool]:
        return await sync_to_async(self.get_or_create)(defaults=defaults, **kwargs)

    async def aupdate_or_create(self, defaults=None, **kwargs) -> tuple[_M, bool]:
        return await sync_to_async(self.update_or_create)(defaults=defaults, **kwargs)

    async def acount(self) -> int:
        return await sync_to_async(self.count)()

    async def aexists(self) -> bool:
        return await sync_to_async(self.exists)()

    def __iter__(self) -> Iterator[_M]:
        return cast("Iterator[_M]", super().__iter__())

    def filter(self, *args, **kwargs) -> Union[AQuerySet[_M], QuerySet[_M]]:
        return super().filter(*args, **kwargs)

    def exclude(self, *args, **kwargs) -> Union[AQuerySet[_M], QuerySet[_M]]:
        return super().exclude(*args, **kwargs)

    def prefetch_related(self, *lookups) -> Union[AQuerySet[_M], QuerySet[_M]]:
        return super().prefetch_related(*lookups)

    def select_related(self, *fields) -> Union[AQuerySet[_M], QuerySet[_M]]:
        return super().select_related(*fields)

    def only(self, *fields) -> Union[AQuerySet[_M], QuerySet[_M]]:
        return super().only(*fields)

    def annotate(self, *args, **kwargs) -> Union[AQuerySet[_M], QuerySet[_M]]:
        return super().annotate(*args, **kwargs)
