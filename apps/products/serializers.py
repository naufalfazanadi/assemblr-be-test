from rest_framework import serializers

from common.serializers import StrictMixin
from .models import Product
from .services import SORTABLE_FIELDS

SORT_CHOICES = [f for f in SORTABLE_FIELDS] + [f'-{f}' for f in SORTABLE_FIELDS]


class ProductListQuerySerializer(StrictMixin, serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=False, max_length=255)
    sort = serializers.ChoiceField(choices=SORT_CHOICES, required=False)
    page = serializers.IntegerField(required=False, min_value=1)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=100)


class ProductSerializer(StrictMixin, serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=12, decimal_places=0)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
