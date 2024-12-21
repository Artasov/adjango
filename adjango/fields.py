from django.db.models.fields.related import ForeignKey, OneToOneField, ManyToManyField

from adjango.descriptors import (
    AForeignKeyDescriptor,
    AOneToOneDescriptor,
    AManyToManyDescriptor
)


class AForeignKey(ForeignKey):
    def contribute_to_class(self, cls, name, private_only=False, **kwargs):
        # Вызов метода родительского класса для стандартной инициализации
        super().contribute_to_class(cls, name, private_only=private_only, **kwargs)
        # Установка кастомного дескриптора на основном классе модели
        setattr(cls, name, AForeignKeyDescriptor(self.remote_field))


class AOneToOneField(OneToOneField):
    def contribute_to_class(self, cls, name, private_only=False, **kwargs):
        # Вызов метода родительского класса для стандартной инициализации
        super().contribute_to_class(cls, name, private_only=private_only, **kwargs)
        # Установка кастомного дескриптора на основном классе модели
        setattr(cls, name, AOneToOneDescriptor(self.remote_field))


class AManyToManyField(ManyToManyField):
    def contribute_to_class(self, cls, name, private_only=False, **kwargs):
        # Вызов метода родительского класса для стандартной инициализации
        super().contribute_to_class(cls, name, private_only=private_only, **kwargs)
        # Установка кастомного дескриптора на основном классе модели
        setattr(cls, name, AManyToManyDescriptor(self.remote_field))
