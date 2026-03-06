import time
import secrets
import uuid
from django.conf import settings
from django.db import models


def generate_order_id():
    timestamp = time.strftime("%Y%m%d%H%M%S")
    random_str = secrets.token_hex(2).upper()
    return f"ORDER-{timestamp}-{random_str}"


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PAID = 'paid', 'Paid'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'
    EXPIRED = 'expired', 'Expired'


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=50, unique=True, default=generate_order_id)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING, db_index=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    midtrans_token = models.CharField(max_length=255, blank=True, null=True)
    midtrans_redirect_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return self.order_id


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f"{self.order.order_id} - {self.product.name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
