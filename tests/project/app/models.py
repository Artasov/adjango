# app/models.py
from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CharField, ForeignKey,
    CASCADE, Model, DecimalField
)

from adjango.fields import AManyToManyField
from adjango.managers.base import AManager
from adjango.models import AModel
from adjango.services.base import ABaseService


class User(AbstractUser, ABaseService):
    phone = CharField(max_length=20, unique=True)


class Product(AModel):
    name = CharField(max_length=100)
    price = DecimalField(max_digits=10, decimal_places=2)


class Order(AModel):
    user = ForeignKey(User, CASCADE)
    products = AManyToManyField(Product)
