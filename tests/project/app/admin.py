# app/admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Order, Product, User


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
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'is_staff',
    )
    search_fields = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'middle_name',
        'phone',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    list_per_page = 50
    list_display_links = ('id', 'email')

    fieldsets = (
        (
            _('General info'),
            {
                'fields': (
                    'id',
                    'username',
                    'first_name',
                    'last_name',
                    'email',
                    'password',
                )
            },
        ),
        (
            _('Roles'),
            {'fields': ('roles',)},
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            },
        ),
        (_('Dates'), {'fields': ('last_login', 'date_joined')}),
    )
