from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class PolymorphicTypeAdminMixin:
    def type(self, obj):
        if obj.polymorphic_ctype:
            return obj.polymorphic_ctype.name
        return _('Unknown')

    type.short_description = _('Type')

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)  # noqa
        return tuple(list_filter) + (('polymorphic_ctype', admin.RelatedOnlyFieldListFilter),)

    def get_list_display(self, request):
        list_display = super().get_list_display(request)  # noqa
        return list_display + ('type',)
