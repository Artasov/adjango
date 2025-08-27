# managers/polymorphic.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Iterable, Type, TypeVar, Union

if TYPE_CHECKING:
    pass

try:
    from django.db.models import Model
    from polymorphic.managers import PolymorphicManager
    from polymorphic.query import PolymorphicQuerySet

    from adjango.querysets.polymorphic import APolymorphicQuerySet

    # Type variable for generic polymorphic manager
    _M = TypeVar("_M", bound=Model)


    class APolymorphicManager(PolymorphicManager, Generic[_M]):
        """Enhanced polymorphic manager with proper type hints."""

        def get_queryset(self) -> Union[APolymorphicQuerySet[_M], PolymorphicQuerySet[_M]]:
            qs = APolymorphicQuerySet(self.model, using=self._db, hints=self._hints)
            if self.model._meta.proxy:
                qs = qs.instance_of(self.model)
            return qs

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

        def getorn(self, exception: Type[Exception] | Exception | None = None, *args: Any, **kwargs: Any) -> _M | None:
            """Get object or return None if not found."""
            return self.get_queryset().getorn(exception, *args, **kwargs)

        async def agetorn(
                self, exception: Type[Exception] | Exception | None = None, *args: Any, **kwargs: Any
        ) -> _M | None:
            """Async get object or return None if not found."""
            return await self.get_queryset().agetorn(exception, *args, **kwargs)

        def all(self) -> Union[APolymorphicQuerySet[_M], PolymorphicQuerySet[_M]]:
            return super().all()

        def filter(self, *args: Any, **kwargs: Any) -> Union[APolymorphicQuerySet[_M], PolymorphicQuerySet[_M]]:
            return super().filter(*args, **kwargs)

        def exclude(self, *args: Any, **kwargs: Any) -> Union[APolymorphicQuerySet[_M], PolymorphicQuerySet[_M]]:
            return super().exclude(*args, **kwargs)

        def prefetch_related(self, *lookups: Any) -> Union[APolymorphicQuerySet[_M], PolymorphicQuerySet[_M]]:
            return super().prefetch_related(*lookups)

        def select_related(self, *fields: Any) -> Union[APolymorphicQuerySet[_M], PolymorphicQuerySet[_M]]:
            return super().select_related(*fields)

        def annotate(self, *fields: Any) -> Union[APolymorphicQuerySet[_M], PolymorphicQuerySet[_M]]:
            return super().annotate(*fields)

except ImportError:
    pass
