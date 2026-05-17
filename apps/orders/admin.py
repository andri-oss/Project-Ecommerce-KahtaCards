from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'shipping_method')
    search_fields = ('order_id', 'user__username', 'recipient_name')
    readonly_fields = ('order_id',)
    inlines = [OrderItemInline]
