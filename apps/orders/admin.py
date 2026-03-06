from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'customer_email']
    readonly_fields = ['order_id', 'midtrans_token', 'midtrans_redirect_url', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
