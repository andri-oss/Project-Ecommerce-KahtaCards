from django.db import models
from django.conf import settings
from apps.catalog.models import Product
import uuid


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Menunggu Pembayaran'
        PAID = 'paid', 'Sudah Dibayar'
        PROCESSING = 'processing', 'Diproses'
        SHIPPED = 'shipped', 'Dikirim'
        DELIVERED = 'delivered', 'Selesai'
        CANCELLED = 'cancelled', 'Dibatalkan'

    class ShippingMethod(models.TextChoices):
        DELIVERY = 'delivery', 'Kirim ke Alamat'
        PICKUP = 'pickup', 'Ambil di Toko'

    order_id = models.CharField(max_length=30, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Shipping info
    shipping_method = models.CharField(
        max_length=20,
        choices=ShippingMethod.choices,
        default=ShippingMethod.DELIVERY
    )
    recipient_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    address = models.TextField()
    save_address = models.BooleanField(default=False)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    # Totals
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_customer_cancel(self):
        """Customers may only self-cancel before the order starts being fulfilled."""
        return self.status in (self.Status.PENDING, self.Status.PAID)

    def get_allowed_next_statuses(self):
        """Statuses an admin is allowed to move this order to, given its current status and shipping method."""
        if self.status in (self.Status.PENDING, self.Status.PAID, self.Status.DELIVERED, self.Status.CANCELLED):
            if self.status == self.Status.PAID:
                if self.shipping_method == self.ShippingMethod.PICKUP:
                    return [self.Status.DELIVERED, self.Status.CANCELLED]
                return [self.Status.PROCESSING, self.Status.CANCELLED]
            return []
        if self.status == self.Status.PROCESSING:
            return [self.Status.SHIPPED, self.Status.CANCELLED]
        if self.status == self.Status.SHIPPED:
            return [self.Status.DELIVERED, self.Status.CANCELLED]
        return []

    def save(self, *args, **kwargs):
        if not self.order_id:
            from django.utils import timezone
            now = timezone.now()
            date_str = now.strftime('%Y%m%d')
            short_uuid = uuid.uuid4().hex[:4].upper()
            self.order_id = f"KHG-{date_str}-{short_uuid}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.order_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    product_image = models.ImageField(upload_to='order_items/', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    variant_info = models.CharField(max_length=255, blank=True)

    # Design data (carried over from CartItem)
    design_file = models.FileField(upload_to='order_designs/', blank=True, null=True)
    design_note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity


class RefundRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Menunggu Diproses'
        COMPLETED = 'completed', 'Refund Selesai'

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='refund_request')
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_holder_name = models.CharField(max_length=150)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Refund #{self.order.order_id}"
