# services/base.py
from django.db.models import Model

from adjango.services.base import ABaseService
from adjango.utils.funcs import arelated


class ABaseModelObjectService:
    service_class: type(ABaseService) = None

    async def arelated(self: Model, field: str):
        return await arelated(self, field)

    @property
    def service(self):
        if not self.service_class:
            raise NotImplementedError('service_class is not defined')
        return self.service_class(self)
