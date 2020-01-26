from django.contrib import admin
from django.utils.formats import localize

from .models import Discount, Payment


class DiscountAdmin(admin.ModelAdmin):
    list_display = ('participant', 'amount', 'created_at', )
    list_display_links = ('amount', )


class DiscountInline(admin.TabularInline):
    model = Discount
    fields = ('amount', 'created_at', )
    readonly_fields = ('amount', 'created_at', )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('troop', 'amount', 'created_at', )
    list_display_links = ('amount', )


class PaymentInline(admin.TabularInline):
    model = Payment
    fields = ('amount', 'created_at', )
    readonly_fields = ('amount', 'created_at', )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(Discount, DiscountAdmin)
admin.site.register(Payment, PaymentAdmin)
