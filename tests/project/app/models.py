# app/models.py

from django.contrib.auth.models import AbstractUser
from django.db.models import CASCADE, CharField, DecimalField, ForeignKey, ManyToManyField
from django.utils.translation import gettext_lazy as _

from adjango.models.base import Model
from adjango.models.mixins import CreatedAtMixin
from adjango.models.polymorphic import PolymorphicModel
from adjango.services.base import BaseService
from models.choices import ATextChoices


class Role(Model):
    class Variant(ATextChoices):
        ORGANIZER = 'org', _('Organizer')
        EVENT_MEMBER = 'event_member', _('Event member')

    name = CharField(max_length=20, unique=True, choices=Variant.choices)

    def __str__(self):
        return str(self.Variant.get_label(self.name))


class UserService(BaseService):
    def __init__(self, user: 'User') -> None:
        super().__init__(user)
        self.user: 'User' = user

    def get_full_name(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'


class User(AbstractUser):
    phone = CharField(max_length=20, unique=True)
    roles = ManyToManyField('Role', related_name='users', blank=True)

    def __str__(self) -> str:
        return self.service.get_full_name()

    @property
    def service(self) -> UserService:
        return UserService(self)


class ProductService(BaseService):
    def __init__(self, obj: 'Product') -> None:
        super().__init__(obj)


class Product(PolymorphicModel, CreatedAtMixin):
    name = CharField(max_length=100)
    price = DecimalField(max_digits=10, decimal_places=2)

    @property
    def service(self) -> ProductService:
        return ProductService(self)


class OrderService(BaseService):
    def __init__(self, obj: 'Order') -> None:
        super().__init__(obj)
        self.order = obj


class Post(Model):
    title = CharField(max_length=100)
    content = CharField(max_length=255)
    image = CharField(max_length=255)


class Order(Model):
    user: User = ForeignKey(User, CASCADE)
    products = ManyToManyField(Product)

    @property
    def service(self) -> OrderService:
        return OrderService(self)
