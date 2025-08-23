# descriptors.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Iterable, Type, TypeVar, cast

from django.db.models.fields.related_descriptors import ManyToManyDescriptor

from adjango.managers.base import AManager

if TYPE_CHECKING:
    from django.db.models import Model

    from adjango.querysets.base import AQuerySet

_RM = TypeVar('_RM', bound='Model')


class AManyRelatedManager(AManager[_RM], Generic[_RM]):
    """Typed base manager for many-to-many relations with async helpers.

    This class is primarily for static typing.  At runtime Django generates a
    concrete ``ManyRelatedManager`` which is combined with this class so that
    all standard manager/queryset methods remain available while adding the
    asynchronous variants provided by :class:`~adjango.managers.base.AManager`.
    """

    # ------------------------------------------------------------------
    # Queryset helpers returning typed ``AQuerySet`` instances
    # ------------------------------------------------------------------
    def get_queryset(self) -> 'AQuerySet[_RM]':  # type: ignore[override]
        from adjango.querysets.base import AQuerySet

        qs = super().get_queryset()
        return cast(AQuerySet[_RM], qs._clone(klass=AQuerySet))

    def all(self) -> 'AQuerySet[_RM]':  # type: ignore[override]
        return cast('AQuerySet[_RM]', super().all())

    def filter(self, *args: Any, **kwargs: Any) -> 'AQuerySet[_RM]':
        return cast('AQuerySet[_RM]', super().filter(*args, **kwargs))

    def exclude(self, *args: Any, **kwargs: Any) -> 'AQuerySet[_RM]':
        return cast('AQuerySet[_RM]', super().exclude(*args, **kwargs))

    def prefetch_related(self, *lookups: Any) -> 'AQuerySet[_RM]':
        return cast('AQuerySet[_RM]', super().prefetch_related(*lookups))

    def select_related(self, *fields: Any) -> 'AQuerySet[_RM]':
        return cast('AQuerySet[_RM]', super().select_related(*fields))

    def only(self, *fields: Any) -> 'AQuerySet[_RM]':
        return cast('AQuerySet[_RM]', super().only(*fields))

    def get(self, *args: Any, **kwargs: Any) -> _RM:  # type: ignore[override]
        return cast(_RM, super().get(*args, **kwargs))

    # ------------------------------------------------------------------
    # Many-to-many specific synchronous helpers
    # ------------------------------------------------------------------
    def add(self, *objs: _RM, through_defaults: dict | None = None) -> None:
        super().add(*objs, through_defaults=through_defaults)

    def remove(self, *objs: _RM) -> None:
        super().remove(*objs)

    def clear(self) -> None:  # type: ignore[override]
        super().clear()

    def set(
        self,
        objs: Iterable[_RM],
        *,
        clear: bool = False,
        through_defaults: dict | None = None,
    ) -> None:  # type: ignore[override]
        super().set(objs, clear=clear, through_defaults=through_defaults)

    def create(self, **kwargs: Any) -> _RM:  # type: ignore[override]
        return cast(_RM, super().create(**kwargs))

    def get_or_create(
        self, defaults: dict | None = None, **kwargs: Any
    ) -> tuple[_RM, bool]:  # type: ignore[override]
        return cast(tuple[_RM, bool], super().get_or_create(defaults=defaults, **kwargs))

    def update_or_create(
        self, defaults: dict | None = None, **kwargs: Any
    ) -> tuple[_RM, bool]:  # type: ignore[override]
        return cast(
            tuple[_RM, bool], super().update_or_create(defaults=defaults, **kwargs)
        )

    def getorn(
        self,
        exception: Type[Exception] | Exception | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> _RM | None:
        return cast(_RM | None, super().getorn(exception, *args, **kwargs))

    # ------------------------------------------------------------------
    # Async wrappers delegating to :class:`AManager`
    # ------------------------------------------------------------------
    async def aall(self) -> list[_RM]:
        return cast(list[_RM], await super().aall())

    async def afilter(self, *args: Any, **kwargs: Any) -> list[_RM]:
        return cast(list[_RM], await super().afilter(*args, **kwargs))

    async def aget(self, *args: Any, **kwargs: Any) -> _RM:
        return cast(_RM, await super().aget(*args, **kwargs))

    async def afirst(self) -> _RM | None:
        return cast(_RM | None, await super().afirst())

    async def alast(self) -> _RM | None:
        return cast(_RM | None, await super().alast())

    async def acreate(self, **kwargs: Any) -> _RM:
        return cast(_RM, await super().acreate(**kwargs))

    async def aget_or_create(
        self, defaults: dict | None = None, **kwargs: Any
    ) -> tuple[_RM, bool]:
        return cast(
            tuple[_RM, bool], await super().aget_or_create(defaults=defaults, **kwargs)
        )

    async def aupdate_or_create(
        self, defaults: dict | None = None, **kwargs: Any
    ) -> tuple[_RM, bool]:
        return cast(
            tuple[_RM, bool], await super().aupdate_or_create(defaults=defaults, **kwargs)
        )

    async def acount(self) -> int:
        return await super().acount()

    async def aexists(self) -> bool:
        return await super().aexists()

    async def aset(self, data: Iterable[_RM], *args: Any, **kwargs: Any) -> None:
        await super().aset(data, *args, **kwargs)

    async def aadd(self, data: _RM, *args: Any, **kwargs: Any) -> None:
        await super().aadd(data, *args, **kwargs)

    async def agetorn(
        self,
        exception: Type[Exception] | Exception | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> _RM | None:
        return cast(
            _RM | None, await super().agetorn(exception, *args, **kwargs)
        )


class AManyToManyDescriptor(ManyToManyDescriptor, Generic[_RM]):
    def __get__(
        self, instance: 'Model | None', owner: type | None = None
    ) -> AManyRelatedManager[_RM]:  # type: ignore[override]
        # ``ManyToManyDescriptor`` returns a dynamically created manager.  Casting
        # here preserves the concrete related model type for static analysers.
        return cast(AManyRelatedManager[_RM], super().__get__(instance, owner))

    @property
    def related_manager_cls(self):
        original_manager_cls = super().related_manager_cls
        rel = self.rel
        related_model = rel.related_model if self.reverse else rel.model
        class _AManyRelatedManager(original_manager_cls, AManyRelatedManager[related_model]):
            pass
        return _AManyRelatedManager
