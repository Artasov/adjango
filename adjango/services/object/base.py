# services/object/base.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from django.db.models import Model

from adjango.utils.funcs import arelated

if TYPE_CHECKING:
    from adjango.services.base import ABaseService

ServiceT = TypeVar("ServiceT", bound="ABaseService[Any]")


class ABaseModelObjectService(Generic[ServiceT]):
    service_class: type[ServiceT] | None = None

    async def arelated(self: Model, field: str) -> Any:
        return await arelated(self, field)

    @property
    def service(self) -> ServiceT:
        if not self.service_class:
            raise NotImplementedError(
                f"Define service_class in your model {self.__class__}"
            )
        return self.service_class(self)
