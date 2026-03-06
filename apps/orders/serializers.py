from rest_framework import serializers

from common.serializers import StrictMixin
from .models import Order, OrderItem, OrderStatus
from .services import SORTABLE_FIELDS

SORT_CHOICES = [f for f in SORTABLE_FIELDS] + [f'-{f}' for f in SORTABLE_FIELDS]
STATUS_CHOICES = OrderStatus.values


class OrderListQuerySerializer(StrictMixin, serializers.Serializer):
    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False)
    sort = serializers.ChoiceField(choices=SORT_CHOICES, required=False)
    page = serializers.IntegerField(required=False, min_value=1)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=100)


class OrderItemSerializer(StrictMixin, serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=0, read_only=True)
    price = serializers.DecimalField(max_digits=12, decimal_places=0, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['id', 'price', 'subtotal', 'product_name', 'created_at', 'updated_at']


class OrderItemInputSerializer(StrictMixin, serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(StrictMixin, serializers.Serializer):
    items = OrderItemInputSerializer(many=True, min_length=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=0, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'status', 'total_price',
            'customer_name', 'customer_email',
            'midtrans_token', 'midtrans_redirect_url',
            'items', 'created_at', 'updated_at',
        ]
        read_only_fields = fields
