from django.utils import timezone
from datetime import timedelta

from .models import Order

UNPAID_ORDER_TTL = timedelta(days=1)


def cancel_unpaid_orders():
    """Cancel orders still PENDING (never reached checkout_payment) after UNPAID_ORDER_TTL."""
    cutoff = timezone.now() - UNPAID_ORDER_TTL
    Order.objects.filter(
        status=Order.Status.PENDING,
        created_at__lt=cutoff,
    ).update(status=Order.Status.CANCELLED, updated_at=timezone.now())
