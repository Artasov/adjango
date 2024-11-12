# managers/base.py
from __future__ import annotations

from django.db.models import Manager

from adjango.querysets.base import AQuerySet


class AManager(Manager.from_queryset(AQuerySet)):
    pass
