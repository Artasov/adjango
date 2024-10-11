from django.contrib.auth.models import AbstractUser
from django.db.models import CharField


class User(AbstractUser):
    phone = CharField(max_length=20, unique=True)
