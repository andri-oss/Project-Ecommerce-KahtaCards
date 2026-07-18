from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

# Single source of truth for which dashboard menus exist and their staff-facing labels.
# Keys must match apps.accounts.models.User.MENU_CHOICES.
MENUS = [
    ('dashboard', 'Dashboard'),
    ('products', 'Produk'),
    ('categories', 'Kategori'),
    ('orders', 'Pesanan'),
    ('customers', 'Pelanggan'),
    ('reports', 'Laporan'),
    ('chat', 'Chat'),
]


def dashboard_access_required(menu_key=None):
    """Gate a dashboard view to admins and staff.

    Admins always pass. Staff must have `menu_key` in their menu_access list.
    A view with menu_key=None (e.g. the dashboard home) is open to any admin/staff user.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect_to_login(request.get_full_path(), login_url='/auth/login/')
            if not (user.is_admin or user.is_staff_employee):
                raise PermissionDenied
            if menu_key and not user.has_menu_access(menu_key):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def admin_only_required(view_func):
    """Gate a view to real admins only — used for employee management so staff can't self-escalate."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url='/auth/login/')
        if not user.is_admin:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped
