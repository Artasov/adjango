# managers/base.py
from __future__ import annotations

from asgiref.sync import sync_to_async
from django.contrib.auth.models import UserManager
from django.db.models import Manager

from adjango.querysets.base import AQuerySet


class AManager(Manager.from_queryset(AQuerySet)):
    pass


class AUserManager(UserManager, AManager):
    async def acreate_user(self, **extra_fields):
        return await sync_to_async(self.create_user)(**extra_fields)
