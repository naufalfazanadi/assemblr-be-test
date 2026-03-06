import uuid
from django.db import models


class PaymentLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=255, db_index=True)
    transaction_status = models.CharField(max_length=100)
    status_code = models.CharField(max_length=10)
    gross_amount = models.CharField(max_length=50)
    signature_valid = models.BooleanField()
    raw_payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_id} — {self.transaction_status} ({self.created_at:%Y-%m-%d %H:%M})"
