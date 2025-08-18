# managers/base.py
from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from asgiref.sync import sync_to_async
from django.contrib.auth.models import UserManager
from django.db.models import Manager

from adjango.querysets.base import AQuerySet

if TYPE_CHECKING:
    from django.db.models import Model

# Type variable for generic Manager
_M = TypeVar("_M", bound="Model")


class AManager(Manager.from_queryset(AQuerySet), Generic[_M]):  # type: ignore
    pass


class AUserManager(UserManager, AManager[_M]):
    async def acreate_user(self, **extra_fields) -> _M:
        return await sync_to_async(self.create_user)(**extra_fields)
