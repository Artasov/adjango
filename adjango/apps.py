# apps.py
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ADjangoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "adjango"
    verbose_name = _("ADjango")
