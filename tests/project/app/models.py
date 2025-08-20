# app/models.py

from django.db.models import CASCADE, CharField, DecimalField, ForeignKey

from adjango.fields import AManyToManyField
from adjango.models.base import AAbstractUser, AModel
from adjango.models.polymorphic import APolymorphicModel
from adjango.services.base import ABaseService
from adjango.models.mixins import ACreatedAtMixin


class UserService(ABaseService):
    def __init__(self, user: "User") -> None:
        super().__init__(user)
        self.user: "User" = user

    def get_full_name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class User(AAbstractUser):
    phone = CharField(max_length=20, unique=True)

    def __str__(self) -> str:
        return self.service.get_full_name()

    @property
    def service(self) -> UserService:
        return UserService(self)


class ProductService(ABaseService):
    def __init__(self, obj: "Product") -> None:
        super().__init__(obj)


class Product(APolymorphicModel, ACreatedAtMixin):
    name = CharField(max_length=100)
    price = DecimalField(max_digits=10, decimal_places=2)

    @property
    def service(self) -> ProductService:
        return ProductService(self)


class OrderService(ABaseService):
    def __init__(self, obj: "Order") -> None:
        super().__init__(obj)


class Post(AModel):
    title = CharField(max_length=100)
    content = CharField(max_length=255)
    image = CharField(max_length=255)


class Order(AModel):
    user: User = ForeignKey(User, CASCADE)
    products: AManyToManyField[Product] = AManyToManyField(Product)

    @property
    def service(self) -> OrderService:
        return OrderService(self)
