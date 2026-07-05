# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        STAFF = 'staff', 'Pegawai'
        CUSTOMER = 'customer', 'Customer'

    # Keys must match apps/dashboard/access.MENUS — each toggles a staff user's
    # access to one dashboard menu. Admins bypass this check entirely.
    MENU_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('products', 'Produk'),
        ('categories', 'Kategori'),
        ('orders', 'Pesanan'),
        ('customers', 'Pelanggan'),
        ('reports', 'Laporan'),
    ]

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    menu_access = models.JSONField(default=list, blank=True)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_staff_employee(self):
        return self.role == self.Role.STAFF

    def has_menu_access(self, menu_key):
        """Admins can access every dashboard menu; staff are limited to their assigned menu_access list."""
        if self.is_admin:
            return True
        if self.is_staff_employee:
            return menu_key in (self.menu_access or [])
        return False

    def __str__(self):
        return self.username