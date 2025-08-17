# services/base.py
from typing import Any, Generic, TypeVar

from django.db.models import Model

from adjango.services.base import ABaseService
from adjango.utils.funcs import arelated

ServiceT = TypeVar('ServiceT', bound=ABaseService)


class ABaseModelObjectService(Generic[ServiceT]):
    service_class: type[ServiceT] | None = None

    async def arelated(self: Model, field: str) -> Any:
        return await arelated(self, field)

    @property
    def service(self) -> ServiceT:
        if not self.service_class:
            raise NotImplementedError(f'Define service_class in your model {self.__class__}')
        return self.service_class(self)
