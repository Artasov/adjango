# app/models.py
from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CharField, CASCADE, Model, DecimalField
)

from adjango.fields import AManyToManyField, AForeignKey, AOneToOneField
from adjango.models.base import AModel, AAbstractUser
from adjango.models.polymorphic import APolymorphicModel


class User(AAbstractUser):
    phone = CharField(max_length=20, unique=True)


class Product(APolymorphicModel):
    name = CharField(max_length=100)
    price = DecimalField(max_digits=10, decimal_places=2)


class Order(AModel):
    user = AForeignKey(User, CASCADE, 'orders')
    oto_user = AOneToOneField(User, CASCADE, related_name='ordersoto')
    products = AManyToManyField(Product)
