# models/mixins.py
from typing import Generic, TypeVar

from django.db.models import DateTimeField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from adjango.models import AModel
from adjango.services.base import ABaseService

ServiceT = TypeVar('ServiceT', bound=ABaseService)


class ACreatedAtMixin(AModel[ServiceT], Generic[ServiceT]):
    created_at = DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        abstract = True


class ACreatedAtEditableMixin(AModel[ServiceT], Generic[ServiceT]):
    created_at = DateTimeField(_('Created at'), default=timezone.now)

    class Meta:
        abstract = True


class AUpdatedAtMixin(AModel[ServiceT], Generic[ServiceT]):
    updated_at = DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True


class ACreatedUpdatedAtMixin(
    ACreatedAtMixin[ServiceT],
    AUpdatedAtMixin[ServiceT],
    Generic[ServiceT]
):
    class Meta:
        abstract = True


class ACreatedAtIndexedMixin(AModel[ServiceT], Generic[ServiceT]):
    created_at = DateTimeField(_('Created at'), auto_now_add=True, db_index=True)

    class Meta:
        abstract = True


class AUpdatedAtIndexedMixin(AModel[ServiceT], Generic[ServiceT]):
    updated_at = DateTimeField(_('Updated at'), auto_now=True, db_index=True)

    class Meta:
        abstract = True


class ACreatedUpdatedAtIndexedMixin(
    ACreatedAtIndexedMixin[ServiceT],
    AUpdatedAtIndexedMixin[ServiceT],
    Generic[ServiceT]
):
    class Meta:
        abstract = True
