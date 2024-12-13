from django.db.models import DateTimeField
from django.utils.translation import gettext_lazy as _

from adjango.models import AModel


class ACreatedAtMixin(AModel):
    created_at = DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        abstract = True


class AUpdatedAtMixin(AModel):
    updated_at = DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True


class ACreatedUpdatedAtMixin(ACreatedAtMixin, AUpdatedAtMixin):
    class Meta:
        abstract = True


class ACreatedAtIndexedMixin(AModel):
    created_at = DateTimeField(_('Created at'), auto_now_add=True, db_index=True)

    class Meta:
        abstract = True


class AUpdatedAtIndexedMixin(AModel):
    updated_at = DateTimeField(_('Updated at'), auto_now=True, db_index=True)

    class Meta:
        abstract = True


class ACreatedUpdatedAtIndexedMixin(ACreatedAtIndexedMixin, AUpdatedAtIndexedMixin):
    class Meta:
        abstract = True
