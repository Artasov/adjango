# app/models.py
from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CharField, ForeignKey,
    CASCADE, Model, DecimalField
)

from adjango.fields import AManyToManyField
from adjango.models.base import AModel, AAbstractUser
from adjango.services.base import ABaseService
from adjango.models.polymorphic import APolymorphicModel



class UserService(ABaseService["User"]):
    def __init__(self, obj: "User") -> None:
        super().__init__(obj)


class User(AAbstractUser[UserService]):
    service_class = UserService
    phone = CharField(max_length=20, unique=True)


class Product(APolymorphicModel):
    name = CharField(max_length=100)
    price = DecimalField(max_digits=10, decimal_places=2)


class Order(AModel):
    user = ForeignKey(User, CASCADE)
    products = AManyToManyField(Product)
