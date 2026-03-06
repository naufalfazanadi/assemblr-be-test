from common.exceptions import NotFoundError, ConflictError
from common.query import apply_search, apply_sort
from .models import Product

SORTABLE_FIELDS = {'name', 'price', 'stock', 'created_at'}


def get_all_products(search=None, sort=None):
    qs = Product.objects.all()
    qs = apply_search(qs, search, ['name', 'description'])
    qs = apply_sort(qs, sort, SORTABLE_FIELDS, default='-created_at')
    return qs


def get_product(pk):
    try:
        return Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        raise NotFoundError(f"Product {pk} not found.")


def create_product(validated_data):
    if Product.objects.filter(name__iexact=validated_data['name']).exists():
        raise ConflictError(f"Product '{validated_data['name']}' already exists.")
    return Product.objects.create(**validated_data)


def update_product(product, validated_data):
    for attr, value in validated_data.items():
        setattr(product, attr, value)
    product.save(update_fields=list(validated_data.keys()))
    return product


def delete_product(product):
    product.delete()
