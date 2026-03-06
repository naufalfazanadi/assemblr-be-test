import midtransclient
from django.conf import settings


def get_snap_client():
    return midtransclient.Snap(
        is_production=False,
        server_key=settings.MIDTRANS_SERVER_KEY,
        client_key=settings.MIDTRANS_CLIENT_KEY,
    )


def create_snap_transaction(order):
    """
    Call Midtrans Snap API to create a payment transaction.
    Returns dict with 'token' and 'redirect_url', or None on failure.
    """
    snap = get_snap_client()

    item_details = []
    for item in order.items.select_related('product').all():
        item_details.append({
            'id': str(item.product.id),
            'price': int(item.price),
            'quantity': item.quantity,
            'name': item.product.name[:50],
        })

    params = {
        'transaction_details': {
            'order_id': order.order_id,
            'gross_amount': int(order.total_price),
        },
        'customer_details': {
            'first_name': order.customer_name,
            'email': order.customer_email,
        },
        'item_details': item_details,
    }

    try:
        result = snap.create_transaction(params)
        return result
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Midtrans Snap error for order {order.order_id}: {e}")
        return None
