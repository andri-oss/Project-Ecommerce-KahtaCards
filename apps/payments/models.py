from django.db import models
from apps.orders.models import Order


class Payment(models.Model):
    class Method(models.TextChoices):
        BCA_VA = 'bca_va', 'BCA Virtual Account'
        MANDIRI_BILL = 'mandiri_bill', 'Mandiri Bill'
        QRIS = 'qris', 'QRIS'
        GOPAY = 'gopay', 'GoPay'
        OVO = 'ovo', 'OVO'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Menunggu'
        COMPLETED = 'completed', 'Berhasil'
        FAILED = 'failed', 'Gagal'
        EXPIRED = 'expired', 'Kadaluarsa'

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    paid_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.order.order_id} — {self.get_method_display()}"
