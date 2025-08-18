# querysets/base.py
from __future__ import annotations

from typing import Any, Type

from django.db.models import QuerySet

from adjango.utils.funcs import aadd, aall, afilter, agetorn, aset, getorn


class AQuerySet(QuerySet):
    async def aall(self):
        return await aall(self)

    def getorn(self, exception: Type[Exception] | None = None, *args, **kwargs) -> Any:
        return getorn(self, exception, *args, **kwargs)

    async def agetorn(
        self, exception: Type[Exception] | None = None, *args, **kwargs
    ) -> Any:
        return await agetorn(self, exception, *args, **kwargs)

    async def afilter(self, *args, **kwargs) -> list:
        return await afilter(self, *args, **kwargs)

    async def aset(self, data, *args, **kwargs) -> None:
        return await aset(self, data, *args, **kwargs)

    async def aadd(self, data, *args, **kwargs) -> None:
        return await aadd(self, data, *args, **kwargs)
