import logging
from decimal import Decimal
from django.db import transaction, IntegrityError

from apps.products.models import Product
from apps.payments.midtrans_client import create_snap_transaction
from common.exceptions import NotFoundError, ValidationError, ServiceUnavailableError
from common.query import apply_sort
from .models import Order, OrderItem, OrderStatus

logger = logging.getLogger(__name__)

SORTABLE_FIELDS = {'created_at', 'total_price', 'status'}


def get_order_by_pk(pk, user):
    try:
        qs = Order.objects.prefetch_related('items__product')
        if not user.is_staff:
            qs = qs.filter(user=user)
        return qs.get(pk=pk)
    except Order.DoesNotExist:
        raise NotFoundError('Order not found.')


def get_order_by_order_id(order_id, user):
    try:
        qs = Order.objects.prefetch_related('items__product')
        if not user.is_staff:
            qs = qs.filter(user=user)
        return qs.get(order_id=order_id)
    except Order.DoesNotExist:
        raise NotFoundError('Order not found.')


def get_all_orders(user, status=None, sort=None):
    qs = Order.objects.prefetch_related('items__product')
    if not user.is_staff:
        qs = qs.filter(user=user)

    if status:
        qs = qs.filter(status=status)
    qs = apply_sort(qs, sort, SORTABLE_FIELDS, default='-created_at')
    return qs


def create_order(user, items_data):
    with transaction.atomic():
        product_ids = [item['product_id'] for item in items_data]
        products = {
            p.id: p
            for p in Product.objects.select_for_update().filter(id__in=product_ids)
        }

        for item in items_data:
            product_id = item['product_id']
            if product_id not in products:
                raise NotFoundError(f"Product {product_id} not found.")

            product = products[product_id]
            if product.stock < item['quantity']:
                raise ValidationError(f"Insufficient stock for '{product.name}'. Available: {product.stock}.")

        total_price = 0
        for item in items_data:
            price = products[item['product_id']].price
            quantity = item['quantity']
            total_price += price * quantity

        order = Order.objects.create(
            user=user,
            customer_name=user.name or user.email,
            customer_email=user.email,
            total_price=total_price,
        )

        order_items = []
        for item in items_data:
            product = products[item['product_id']]
            quantity = item['quantity']
            order_items.append(OrderItem(order=order, product=product, quantity=quantity, price=product.price))
            product.stock -= quantity

        OrderItem.objects.bulk_create(order_items)
        Product.objects.bulk_update(products.values(), ['stock'])

    logger.info("Order %s created for user %s", order.order_id, user.email)
    return order


def update_order(order, items_data):
    if order.status != OrderStatus.PENDING:
        raise ValidationError(f"Cannot update an order with status '{order.status}'.")

    with transaction.atomic():
        # Lock all affected products (old + new) together
        old_product_ids = list(order.items.values_list('product_id', flat=True))
        new_product_ids = [item['product_id'] for item in items_data]
        all_product_ids = list(set(old_product_ids) | set(new_product_ids))

        products = {
            p.id: p
            for p in Product.objects.select_for_update().filter(id__in=all_product_ids)
        }

        for item in items_data:
            product_id = item['product_id']
            if product_id not in products:
                raise NotFoundError(f"Product {product_id} not found.")

        # Restore stock from old items
        for item in order.items.all():
            products[item.product_id].stock += item.quantity

        # Validate stock availability and calculate total price
        total_price = 0
        for item in items_data:
            product = products[item['product_id']]
            if product.stock < item['quantity']:
                raise ValidationError(f"Insufficient stock for '{product.name}'. Available: {product.stock}.")
            total_price += product.price * item['quantity']

        # Replace items and deduct stock
        order.items.all().delete()
        order_items = []
        for item in items_data:
            product = products[item['product_id']]
            quantity = item['quantity']
            order_items.append(OrderItem(order=order, product=product, quantity=quantity, price=product.price))
            product.stock -= quantity

        OrderItem.objects.bulk_create(order_items)
        Product.objects.bulk_update(products.values(), ['stock'])

        order.total_price = total_price
        order.save(update_fields=['total_price'])

    logger.info("Order %s updated by user %s", order.order_id, order.user.email)
    return order


def cancel_order(order):
    if order.status != OrderStatus.PENDING:
        raise ValidationError(f"Cannot cancel an order with status '{order.status}'.")

    # Revert stock
    with transaction.atomic():
        product_ids = list(order.items.values_list('product_id', flat=True))
        products = {
            p.id: p
            for p in Product.objects.select_for_update().filter(id__in=product_ids)
        }

        for item in order.items.all():
            products[item.product_id].stock += item.quantity

        Product.objects.bulk_update(products.values(), ['stock'])
        order.status = OrderStatus.CANCELLED
        order.save(update_fields=['status'])

    logger.info("Order %s cancelled, stock restored", order.order_id)
    return order


def attach_payment_token(order):
    snap_data = create_snap_transaction(order)
    if not snap_data:
        logger.warning("Midtrans Snap failed for order %s", order.order_id)
        return order
    order.midtrans_token = snap_data.get('token')
    order.midtrans_redirect_url = snap_data.get('redirect_url')
    order.save(update_fields=['midtrans_token', 'midtrans_redirect_url'])
    return order


def get_payment_token(order):
    if order.status != OrderStatus.PENDING:
        raise ValidationError(f"Cannot generate payment for order with status '{order.status}'.")

    # Reuse existing token to prevent Midtrans duplicate order_id errors
    if order.midtrans_token:
        return order

    order = attach_payment_token(order)
    if not order.midtrans_token:
        raise ServiceUnavailableError("Failed to get payment token. Please try again.")
    return order
