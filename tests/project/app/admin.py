# app/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Order, Product, User


class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        *BaseUserAdmin.fieldsets,
        (
            _("Additional Information"),
            {
                "fields": ("phone",),
            },
        ),
    )
    add_fieldsets = (
        *BaseUserAdmin.add_fieldsets,
        (
            _("Additional Information"),
            {
                "fields": ("phone",),
            },
        ),
    )
    list_display = ("username", "email", "first_name", "last_name", "phone", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "phone")
    ordering = ("username",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    search_fields = ("name",)
    list_filter = ("price",)
    ordering = ("name",)
    readonly_fields = ("id",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__username", "id")
    filter_horizontal = ("products",)


@admin.register(User)
class UserAdmin(CustomUserAdmin):
    pass
