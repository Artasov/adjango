# querysets/base.py
from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Type, TypeVar, Union

from asgiref.sync import sync_to_async
from django.db.models import QuerySet

from adjango.utils.funcs import aadd, agetorn, aset, getorn

if TYPE_CHECKING:
    pass

# Type variable for generic QuerySet
_M = TypeVar("_M", bound="Model")


class AQuerySet(QuerySet[_M], Generic[_M]):
    async def aall(self) -> list[_M]:
        """Возвращает все объекты из QuerySet."""
        return await self._aall_from_queryset(self)

    def getorn(self, exception: Type[Exception] | None = None, *args, **kwargs) -> _M | None:
        return getorn(self, exception, *args, **kwargs)

    async def agetorn(self, exception: Type[Exception] | None = None, *args, **kwargs) -> _M | None:
        return await agetorn(self, exception, *args, **kwargs)

    async def afilter(self, *args, **kwargs) -> list[_M]:
        """Возвращает список объектов после фильтрации."""
        filtered_qs = self.filter(*args, **kwargs)
        return await self._aall_from_queryset(filtered_qs)

    async def _aall_from_queryset(self, queryset) -> list[_M]:
        """Внутренний метод для получения всех объектов из QuerySet."""
        return await sync_to_async(list)(queryset)

    async def aset(self, data, *args, **kwargs) -> None:
        return await aset(self, data, *args, **kwargs)

    async def aadd(self, data, *args, **kwargs) -> None:
        return await aadd(self, data, *args, **kwargs)

    # Добавляем типизированные версии стандартных Django методов
    async def aget(self, *args, **kwargs) -> _M:
        """Асинхронный get - возвращает один объект или выбрасывает исключение."""
        return await sync_to_async(self.get)(*args, **kwargs)

    async def afirst(self) -> _M | None:
        """Асинхронный first - возвращает первый объект или None."""
        return await sync_to_async(self.first)()

    async def alast(self) -> _M | None:
        """Асинхронный last - возвращает последний объект или None."""
        return await sync_to_async(self.last)()

    async def acreate(self, **kwargs) -> _M:
        """Асинхронный create - создает и сохраняет объект."""
        return await sync_to_async(self.create)(**kwargs)

    async def aget_or_create(self, defaults=None, **kwargs) -> tuple[_M, bool]:
        """Асинхронный get_or_create - возвращает кортеж (объект, создан_ли)."""
        return await sync_to_async(self.get_or_create)(defaults=defaults, **kwargs)

    async def aupdate_or_create(self, defaults=None, **kwargs) -> tuple[_M, bool]:
        """Асинхронный update_or_create - возвращает кортеж (объект, создан_ли)."""
        return await sync_to_async(self.update_or_create)(defaults=defaults, **kwargs)

    async def acount(self) -> int:
        """Асинхронный count - возвращает количество объектов."""
        return await sync_to_async(self.count)()

    async def aexists(self) -> bool:
        """Асинхронный exists - проверяет существование объектов."""
        return await sync_to_async(self.exists)()

    def filter(self, *args, **kwargs) -> Union["AQuerySet[_M]", "QuerySet"]:
        """Переопределяем filter чтобы он возвращал правильный тип QuerySet."""
        return super().filter(*args, **kwargs)

    def exclude(self, *args, **kwargs) -> Union["AQuerySet[_M]", "QuerySet"]:
        """Переопределяем exclude чтобы он возвращал правильный тип QuerySet."""
        return super().exclude(*args, **kwargs)

    def prefetch_related(self, *lookups) -> Union["AQuerySet[_M]", "QuerySet"]:
        """Переопределяем prefetch_related чтобы он возвращал правильный тип QuerySet."""
        return super().prefetch_related(*lookups)

    def select_related(self, *fields) -> Union["AQuerySet[_M]", "QuerySet"]:
        """Переопределяем select_related чтобы он возвращал правильный тип QuerySet."""
        return super().select_related(*fields)
