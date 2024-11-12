# services/base.py
from django.db.models import Model

from adjango.utils.funcs import arelated


class ABaseService:
    async def arelated(self: Model, field: str):
        return await arelated(self, field)
