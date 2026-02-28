# models/mixins.py
from __future__ import annotations

from typing import Any

from django.db import transaction
from django.db.models import DateTimeField, FileField
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


class FileCleanupMixin(Model):
    """
    Auto cleanup for FileField/ImageField files on replace/delete.

    Configuration examples:
    - FILE_CLEANUP = True
    - FILE_CLEANUP = False
    - FILE_CLEANUP = {
        '*': {'on_replace': True, 'on_delete': True},
        'avatar': {'on_replace': False},
        'contract': False,
      }
    """

    FILE_CLEANUP: bool | dict[str, bool | dict[str, bool]] = True

    class Meta:
        abstract = True

    @classmethod
    def _file_fields(cls) -> list[FileField]:
        return [field for field in cls._meta.concrete_fields if isinstance(field, FileField)]

    @classmethod
    def _normalize_entry(
            cls,
            entry: bool | dict[str, bool] | None,
            fallback: dict[str, bool],
    ) -> dict[str, bool]:
        if entry is None:
            return dict(fallback)
        if entry is True:
            return {'enabled': True, 'on_replace': True, 'on_delete': True}
        if entry is False:
            return {'enabled': False, 'on_replace': False, 'on_delete': False}
        if not isinstance(entry, dict):
            raise TypeError('FILE_CLEANUP entries must be bool or dict[str, bool]')

        policy = dict(fallback)
        for key in ('enabled', 'on_replace', 'on_delete'):
            if key in entry:
                value = entry[key]
                if not isinstance(value, bool):
                    raise TypeError(f'FILE_CLEANUP["{key}"] must be bool')
                policy[key] = value
        return policy

    @classmethod
    def _field_policy(cls, field_name: str) -> dict[str, bool]:
        default_policy = {'enabled': True, 'on_replace': True, 'on_delete': True}
        config = getattr(cls, 'FILE_CLEANUP', True)

        if config is True:
            return default_policy
        if config is False:
            return {'enabled': False, 'on_replace': False, 'on_delete': False}
        if not isinstance(config, dict):
            raise TypeError('FILE_CLEANUP must be bool or dict[str, bool | dict[str, bool]]')

        base_policy = cls._normalize_entry(config.get('*', True), default_policy)
        return cls._normalize_entry(config.get(field_name), base_policy)

    @staticmethod
    def _schedule_delete(storage: Any, name: str) -> None:
        if not name:
            return
        transaction.on_commit(lambda: storage.delete(name))

    def _collect_replaced_files(self) -> list[tuple[Any, str]]:
        if not self.pk:
            return []

        fields = self._file_fields()
        if not fields:
            return []

        field_names = [field.name for field in fields]
        old_values = self.__class__.objects.filter(pk=self.pk).values(*field_names).first()
        if not old_values:
            return []

        to_delete: list[tuple[Any, str]] = []
        for field in fields:
            policy = self._field_policy(field.name)
            if not (policy['enabled'] and policy['on_replace']):
                continue

            old_name = old_values.get(field.name)
            new_file = getattr(self, field.name)
            new_name = getattr(new_file, 'name', None)

            if old_name and old_name != new_name:
                to_delete.append((field.storage, old_name))

        return to_delete

    def _collect_deleted_files(self) -> list[tuple[Any, str]]:
        to_delete: list[tuple[Any, str]] = []
        for field in self._file_fields():
            policy = self._field_policy(field.name)
            if not (policy['enabled'] and policy['on_delete']):
                continue

            file_obj = getattr(self, field.name)
            name = getattr(file_obj, 'name', None)
            if name:
                to_delete.append((field.storage, name))
        return to_delete

    def save(self, *args: Any, **kwargs: Any) -> None:
        to_delete = self._collect_replaced_files()
        super().save(*args, **kwargs)
        for storage, name in to_delete:
            self._schedule_delete(storage, name)

    def delete(self, *args: Any, **kwargs: Any) -> None:
        to_delete = self._collect_deleted_files()
        super().delete(*args, **kwargs)
        for storage, name in to_delete:
            self._schedule_delete(storage, name)
