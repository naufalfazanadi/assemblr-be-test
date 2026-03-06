from django.contrib import admin
from .models import PaymentLog


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'transaction_status', 'status_code', 'gross_amount', 'signature_valid', 'created_at']
    list_filter = ['transaction_status', 'signature_valid']
    search_fields = ['order_id']
    readonly_fields = ['id', 'order_id', 'transaction_status', 'status_code', 'gross_amount', 'signature_valid', 'raw_payload', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
