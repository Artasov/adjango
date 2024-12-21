# adjango/descriptors.py
from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields.related_descriptors import (
    ManyToManyDescriptor,
    ForwardManyToOneDescriptor,
    ReverseOneToOneDescriptor,
)

from adjango.managers.base import AManager
from adjango.utils.base import is_async_context


class AForeignKeyDescriptor(ForwardManyToOneDescriptor):
    def __get__(self, instance, cls=None) -> Any:
        if instance is None:
            return self

        if is_async_context():
            fk_attname = self.field.field.attname
            if not fk_attname:
                raise AttributeError(f"ForeignObjectRel '{self.field}' does not have 'field.attname'")

            fk_value = getattr(instance, fk_attname, None)
            if fk_value is None:
                return None

            async def get_related():
                related_model = self.field.field.related_model
                try:
                    obj = await related_model.objects.aget(pk=fk_value)
                    return obj
                except ObjectDoesNotExist:
                    return None

            return get_related()
        else:
            return super().__get__(instance, cls)


class AOneToOneDescriptor(ReverseOneToOneDescriptor):
    def __get__(self, instance, cls=None) -> Any:
        if instance is None:
            return self

        if is_async_context():
            related_attname = self.related.field.attname
            if not related_attname:
                raise AttributeError(f"OneToOneObjectRel '{self.related}' does not have 'field.attname'")

            related_id = getattr(instance, related_attname, None)
            if related_id is None:
                return None

            async def get_related():
                related_model = self.related.model
                try:
                    obj = await related_model.objects.aget(pk=related_id)
                    return obj
                except ObjectDoesNotExist:
                    return None

            return get_related()
        else:
            return super().__get__(instance, cls)


class AManyToManyDescriptor(ManyToManyDescriptor):
    def __get__(self, instance, cls=None) -> Any:
        print(3)  # Для проверки вызова дескриптора
        if instance is None:
            return self

        # Получаем стандартный менеджер
        related_manager = super().__get__(instance, cls)
        print(related_manager)

        if is_async_context():
            # Создаём новый класс менеджера, наследующийся от стандартного и AManager
            class AManyRelatedManager(related_manager.__class__, AManager):
                pass

            # Возвращаем экземпляр менеджера с переданным instance и полем
            return AManyRelatedManager(instance, self.field)
        else:
            return related_manager
