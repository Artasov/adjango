# models/mixins.py
from django.db.models import DateTimeField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from adjango.models import Model


class CreatedAtMixin(Model):
    created_at = DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        abstract = True


class CreatedAtEditableMixin(Model):
    created_at = DateTimeField(_('Created at'), default=timezone.now)

    class Meta:
        abstract = True


class UpdatedAtMixin(Model):
    updated_at = DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True


class CreatedUpdatedAtMixin(CreatedAtMixin, UpdatedAtMixin):
    class Meta:
        abstract = True


class CreatedAtIndexedMixin(Model):
    created_at = DateTimeField(_('Created at'), auto_now_add=True, db_index=True)

    class Meta:
        abstract = True


class UpdatedAtIndexedMixin(Model):
    updated_at = DateTimeField(_('Updated at'), auto_now=True, db_index=True)

    class Meta:
        abstract = True


class CreatedUpdatedAtIndexedMixin(
    CreatedAtIndexedMixin,
    UpdatedAtIndexedMixin,
):
    class Meta:
        abstract = True
