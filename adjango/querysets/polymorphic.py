# querysets/polymorphic.py
try:
    from typing import TYPE_CHECKING, Generic, TypeVar

    from polymorphic.query import PolymorphicQuerySet

    from adjango.querysets.base import AQuerySet
    from adjango.utils.funcs import aadd, aall, afilter, agetorn, aset, getorn

    if TYPE_CHECKING:
        from django.db.models import Model

    # Type variable for polymorphic QuerySet
    _M = TypeVar("_M", bound="Model")

    class APolymorphicQuerySet(AQuerySet[_M], PolymorphicQuerySet, Generic[_M]):
        async def aall(self) -> list[_M]:
            """Returns all objects from QuerySet."""
            return await self._aall_from_queryset(self)

        def getorn(self, exception=None, *args, **kwargs) -> _M | None:
            return getorn(self, exception, *args, **kwargs)

        async def agetorn(self, exception=None, *args, **kwargs) -> _M | None:
            return await agetorn(self, exception, *args, **kwargs)

        async def afilter(self, *args, **kwargs) -> list[_M]:
            """Returns list of objects after filtering."""
            filtered_qs = self.filter(*args, **kwargs)
            return await self._aall_from_queryset(filtered_qs)

        async def aset(self, data, *args, **kwargs) -> None:
            return await aset(self, data, *args, **kwargs)

        async def aadd(self, data, *args, **kwargs) -> None:
            return await aadd(self, data, *args, **kwargs)

except ImportError:
    pass
