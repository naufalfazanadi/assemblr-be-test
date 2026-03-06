import hashlib
import logging
from django.conf import settings

from apps.orders.models import Order, OrderStatus
from common.exceptions import PermissionDeniedError, NotFoundError
from .models import PaymentLog

logger = logging.getLogger(__name__)

TERMINAL_STATUSES = {OrderStatus.PAID, OrderStatus.FAILED, OrderStatus.CANCELLED, OrderStatus.EXPIRED}

MIDTRANS_STATUS_MAP = {
    'settlement': OrderStatus.PAID,
    'capture': OrderStatus.PAID,
    'cancel': OrderStatus.CANCELLED,
    'expire': OrderStatus.EXPIRED,
    'deny': OrderStatus.FAILED,
    'failure': OrderStatus.FAILED,
}


def process_webhook(payload):
    order_id = payload.get('order_id', '')
    status_code = payload.get('status_code', '')
    gross_amount = payload.get('gross_amount', '')
    signature_key = payload.get('signature_key', '')
    transaction_status = payload.get('transaction_status', '')

    signature_valid = _verify_signature(order_id, status_code, gross_amount, signature_key)

    PaymentLog.objects.create(
        order_id=order_id,
        transaction_status=transaction_status,
        status_code=status_code,
        gross_amount=gross_amount,
        signature_valid=signature_valid,
        raw_payload=payload,
    )

    if not signature_valid:
        logger.warning("Invalid Midtrans signature for order %s", order_id)
        raise PermissionDeniedError("Invalid signature.")

    if order_id.startswith('payment_notif_test_'):
        logger.info("Midtrans test notification received, skipping order lookup.")
        return 'skipped'

    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        raise NotFoundError(f"Order {order_id} not found.")

    if order.status in TERMINAL_STATUSES:
        return 'skipped'

    new_status = MIDTRANS_STATUS_MAP.get(transaction_status)
    if new_status:
        if new_status in {OrderStatus.FAILED, OrderStatus.CANCELLED, OrderStatus.EXPIRED}:
            from django.db import transaction
            from apps.products.models import Product
            with transaction.atomic():
                product_ids = list(order.items.values_list('product_id', flat=True))
                products = {
                    p.id: p
                    for p in Product.objects.select_for_update().filter(id__in=product_ids)
                }

                for item in order.items.all():
                    products[item.product_id].stock += item.quantity

                Product.objects.bulk_update(products.values(), ['stock'])
                order.status = new_status
                order.save(update_fields=['status'])
                logger.info("Order %s status updated to %s, stock restored", order_id, new_status)
        else:
            order.status = new_status
            order.save(update_fields=['status'])
            logger.info("Order %s status updated to %s", order_id, new_status)

    return 'processed'


def _verify_signature(order_id, status_code, gross_amount, signature_key):
    raw = f"{order_id}{status_code}{gross_amount}{settings.MIDTRANS_SERVER_KEY}"
    expected = hashlib.sha512(raw.encode()).hexdigest()
    return expected == signature_key
