# app/models.py
from django.db.models import CharField, ForeignKey, CASCADE, DecimalField

from adjango.fields import AManyToManyField
from adjango.models.base import AModel, AAbstractUser
from adjango.models.polymorphic import APolymorphicModel
from adjango.services.base import ABaseService


class UserService(ABaseService["User"]):
    def __init__(self, obj: "User") -> None:
        super().__init__(obj)

    def get_full_name(self) -> str:
        return f"{self.obj.first_name} {self.obj.last_name}"


class User(AAbstractUser[UserService]):
    service_class = UserService
    phone = CharField(max_length=20, unique=True)

    def __str__(self) -> str:
        return self.service.get_full_name()


class Product(APolymorphicModel):
    name = CharField(max_length=100)
    price = DecimalField(max_digits=10, decimal_places=2)


class Order(AModel):
    user = ForeignKey(User, CASCADE)
    products = AManyToManyField(Product)
