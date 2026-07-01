import csv

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.orders.models import Order, OrderItem, RefundRequest
from apps.catalog.models import Product, Category
from apps.accounts.models import User
from apps.payments.models import Payment
from .access import dashboard_access_required, admin_only_required, MENUS

PAID_STATUSES = ['paid', 'processing', 'shipped', 'delivered']


def _reports_queryset(request):
    """Shared date-filtered, paid-orders queryset for the transaction report + its CSV export."""
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    orders = Order.objects.select_related('user').filter(status__in=PAID_STATUSES).order_by('-created_at')

    if start_date:
        orders = orders.filter(created_at__date__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__date__lte=end_date)

    return orders, start_date, end_date


@dashboard_access_required()
def dashboard_view(request):
    """Admin overview — stats cards, revenue chart, recent orders."""
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Stats
    total_orders_today = Order.objects.filter(created_at__date=today).count()
    revenue_month = Order.objects.filter(
        created_at__date__gte=month_start,
        status__in=['paid', 'processing', 'shipped', 'delivered']
    ).aggregate(total=Sum('total'))['total'] or 0

    new_orders = Order.objects.filter(status='pending').count()
    active_products = Product.objects.filter(is_active=True).count()

    # Order status distribution
    status_counts = {
        'delivered': Order.objects.filter(status='delivered').count(),
        'processing': Order.objects.filter(status__in=['paid', 'processing', 'shipped']).count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
    }

    # Revenue per day (last 7 days)
    revenue_days = []
    day_labels = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        day_total = Order.objects.filter(
            created_at__date=d,
            status__in=['paid', 'processing', 'shipped', 'delivered']
        ).aggregate(t=Sum('total'))['t'] or 0
        revenue_days.append({
            'label': day_labels[d.weekday()],
            'value': int(day_total),
        })

    # Recent orders
    recent_orders = Order.objects.select_related('user', 'refund_request').order_by('-created_at')[:10]

    context = {
        'total_orders_today': total_orders_today,
        'revenue_month': revenue_month,
        'new_orders': new_orders,
        'active_products': active_products,
        'status_counts': status_counts,
        'revenue_days': revenue_days,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/index.html', context)


@dashboard_access_required('products')
def products_view(request):
    """Product management list."""
    search = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')

    products = Product.objects.select_related('category').order_by('-created_at')

    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(slug__icontains=search)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)

    paginator = Paginator(products, 10)
    page = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()

    return render(request, 'dashboard/products.html', {
        'page_obj': page,
        'categories': categories,
        'search': search,
        'selected_category': category_slug,
    })


@dashboard_access_required('products')
def product_add_view(request):
    """Add a new product."""
    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        price = request.POST.get('price', '0')
        min_order = request.POST.get('min_order', '1')
        description = request.POST.get('description', '')
        material_spec = request.POST.get('material_spec', '')
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')

        # Auto-generate slug
        from django.utils.text import slugify
        slug = slugify(name)
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        try:
            product = Product(
                name=name,
                slug=slug,
                category_id=int(category_id),
                price=int(price),
                min_order=int(min_order),
                description=description,
                material_spec=material_spec,
                is_active=is_active,
            )
            if image:
                product.image = image
            product.save()
            return redirect('dashboard:products')
        except Exception as e:
            return render(request, 'dashboard/product_form.html', {
                'categories': categories,
                'error': str(e),
                'form_data': request.POST,
            })

    return render(request, 'dashboard/product_form.html', {
        'categories': categories,
    })


@dashboard_access_required('products')
def product_edit_view(request, pk):
    """Edit an existing product."""
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()

    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip()
        product.category_id = int(request.POST.get('category'))
        product.price = int(request.POST.get('price', '0'))
        product.min_order = int(request.POST.get('min_order', '1'))
        product.description = request.POST.get('description', '')
        product.material_spec = request.POST.get('material_spec', '')
        product.is_active = request.POST.get('is_active') == 'on'

        if request.FILES.get('image'):
            product.image = request.FILES['image']

        # Update slug if name changed
        from django.utils.text import slugify
        new_slug = slugify(product.name)
        if new_slug != product.slug:
            base_slug = new_slug
            counter = 1
            while Product.objects.filter(slug=new_slug).exclude(pk=pk).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            product.slug = new_slug

        try:
            product.save()
            return redirect('dashboard:products')
        except Exception as e:
            return render(request, 'dashboard/product_form.html', {
                'product': product,
                'categories': categories,
                'error': str(e),
            })

    return render(request, 'dashboard/product_form.html', {
        'product': product,
        'categories': categories,
    })


@dashboard_access_required('products')
def product_toggle_view(request, pk):
    """Toggle product active status (AJAX)."""
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        product.is_active = not product.is_active
        product.save(update_fields=['is_active', 'updated_at'])
        return JsonResponse({
            'success': True,
            'is_active': product.is_active,
        })
    return JsonResponse({'success': False}, status=400)


@dashboard_access_required('products')
def product_delete_view(request, pk):
    """Delete a product."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('dashboard:products')
    return redirect('dashboard:products')


@dashboard_access_required('categories')
def categories_view(request):
    """Category management — list + inline add."""
    from django.utils.text import slugify

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '')
        image = request.FILES.get('image')

        if name:
            slug = slugify(name)
            base_slug = slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            cat = Category(name=name, slug=slug, description=description)
            if image:
                cat.image = image
            cat.save()
        return redirect('dashboard:categories')

    categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('-created_at')

    return render(request, 'dashboard/categories.html', {
        'categories': categories,
    })


@dashboard_access_required('categories')
def category_edit_view(request, pk):
    """Edit a category."""
    from django.utils.text import slugify

    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name', '').strip()
        category.description = request.POST.get('description', '')
        if request.FILES.get('image'):
            category.image = request.FILES['image']

        new_slug = slugify(category.name)
        if new_slug != category.slug:
            base_slug = new_slug
            counter = 1
            while Category.objects.filter(slug=new_slug).exclude(pk=pk).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            category.slug = new_slug

        category.save()
        return redirect('dashboard:categories')

    return render(request, 'dashboard/category_form.html', {
        'category': category,
    })


@dashboard_access_required('categories')
def category_delete_view(request, pk):
    """Delete a category (AJAX)."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        product_count = category.products.count()
        if product_count > 0:
            return JsonResponse({
                'success': False,
                'error': f'Kategori masih memiliki {product_count} produk. Hapus atau pindahkan produk terlebih dahulu.'
            }, status=400)
        category.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('dashboard:categories')
    return redirect('dashboard:categories')


@dashboard_access_required('orders')
def orders_view(request):
    """Order management list with filters."""
    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '')

    orders = Order.objects.select_related('user', 'refund_request').order_by('-created_at')

    if status_filter == 'refund_pending':
        orders = orders.filter(refund_request__status=RefundRequest.Status.PENDING)
    elif status_filter:
        orders = orders.filter(status=status_filter)
    if search:
        orders = orders.filter(
            Q(order_id__icontains=search) |
            Q(user__username__icontains=search) |
            Q(recipient_name__icontains=search)
        )

    paginator = Paginator(orders, 10)
    page = paginator.get_page(request.GET.get('page'))

    # Summary stats
    summary = {
        'pending': Order.objects.filter(status='pending').count(),
        'processing': Order.objects.filter(status__in=['paid', 'processing']).count(),
        'shipped': Order.objects.filter(status='shipped').count(),
        'delivered': Order.objects.filter(status='delivered').count(),
        'refund_pending': RefundRequest.objects.filter(status=RefundRequest.Status.PENDING).count(),
    }

    return render(request, 'dashboard/orders.html', {
        'page_obj': page,
        'status_filter': status_filter,
        'search': search,
        'summary': summary,
    })


@dashboard_access_required('orders')
def order_detail_view(request, pk):
    """Single order detail with update capability."""
    order = get_object_or_404(Order.objects.select_related('user'), pk=pk)
    items = order.items.select_related('product').all()

    try:
        payment = order.payment
    except Payment.DoesNotExist:
        payment = None

    try:
        refund_request = order.refund_request
    except RefundRequest.DoesNotExist:
        refund_request = None

    return render(request, 'dashboard/order_detail.html', {
        'order': order,
        'items': items,
        'payment': payment,
        'refund_request': refund_request,
        'allowed_next_statuses': order.get_allowed_next_statuses(),
    })


@dashboard_access_required('orders')
def order_update_status(request, pk):
    """AJAX: update order status."""
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk)
        import json
        data = json.loads(request.body)
        new_status = data.get('status')
        tracking_number = data.get('tracking_number')

        if new_status in order.get_allowed_next_statuses():
            order.status = new_status
            if tracking_number:
                order.tracking_number = tracking_number
            order.save(update_fields=['status', 'tracking_number', 'updated_at'])
            return JsonResponse({
                'success': True,
                'status': order.status,
                'status_display': order.get_status_display()
            })
    return JsonResponse({'success': False}, status=400)


@dashboard_access_required('orders')
def refund_mark_completed(request, pk):
    """AJAX: mark a customer's refund request as completed after manual bank transfer."""
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=400)

    refund = get_object_or_404(RefundRequest, order__pk=pk)

    proof_image = request.FILES.get('proof_image')
    if not proof_image:
        return JsonResponse({'success': False, 'error': 'Bukti transfer wajib diunggah.'}, status=400)

    refund.proof_image = proof_image
    refund.status = RefundRequest.Status.COMPLETED
    refund.processed_at = timezone.now()
    refund.save(update_fields=['proof_image', 'status', 'processed_at'])

    return JsonResponse({'success': True})


@dashboard_access_required('customers')
def customers_view(request):
    """Customer management list."""
    search = request.GET.get('q', '')
    customers = User.objects.annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total')
    ).order_by('-date_joined')

    if search:
        customers = customers.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    paginator = Paginator(customers, 10)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/customers.html', {
        'page_obj': page,
        'search': search,
    })


@dashboard_access_required('reports')
def reports_view(request):
    """Transaction report — order/revenue stats, transaction list, and top customers for a date range."""
    orders, start_date, end_date = _reports_queryset(request)

    stats = orders.aggregate(total_revenue=Sum('total'), total_orders=Count('id'))
    total_orders = stats['total_orders'] or 0
    total_revenue = stats['total_revenue'] or 0
    avg_order_value = total_revenue / total_orders if total_orders else 0

    top_customers = orders.values('user__id', 'user__username', 'user__first_name', 'user__last_name').annotate(
        order_count=Count('id'),
        total_spent=Sum('total'),
    ).order_by('-total_spent')[:10]

    paginator = Paginator(orders, 15)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/reports.html', {
        'page_obj': page,
        'start_date': start_date,
        'end_date': end_date,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'top_customers': top_customers,
    })


@dashboard_access_required('reports')
def reports_export_csv(request):
    """Export the currently filtered transaction report as CSV."""
    orders, start_date, end_date = _reports_queryset(request)

    response = HttpResponse(content_type='text/csv')
    filename = f"laporan-transaksi_{start_date or 'awal'}_{end_date or 'akhir'}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['No. Pesanan', 'Pelanggan', 'Tanggal', 'Status', 'Metode Pengiriman', 'Total'])
    for order in orders:
        writer.writerow([
            order.order_id,
            order.recipient_name or order.user.username,
            order.created_at.strftime('%Y-%m-%d %H:%M'),
            order.get_status_display(),
            order.get_shipping_method_display(),
            int(order.total),
        ])

    return response


@admin_only_required
def employees_view(request):
    """List staff/employee accounts — admin-only so staff can't manage their own access."""
    search = request.GET.get('q', '')
    employees = User.objects.filter(role=User.Role.STAFF).order_by('-date_joined')

    if search:
        employees = employees.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    paginator = Paginator(employees, 10)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/employees.html', {
        'page_obj': page,
        'search': search,
        'menus': MENUS,
    })


@admin_only_required
def employee_add_view(request):
    """Create a new staff/employee account with a chosen menu_access set."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        menu_access = request.POST.getlist('menu_access')

        error = None
        if not username or not password:
            error = 'Username dan password wajib diisi.'
        elif User.objects.filter(username=username).exists():
            error = 'Username sudah digunakan.'

        if error:
            return render(request, 'dashboard/employee_form.html', {
                'error': error,
                'menus': MENUS,
                'form_data': request.POST,
            })

        employee = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=User.Role.STAFF,
            is_staff=True,
            is_active=True,
            menu_access=[m for m in menu_access if m in dict(MENUS)],
        )
        employee.set_password(password)
        employee.save()
        return redirect('dashboard:employees')

    return render(request, 'dashboard/employee_form.html', {
        'menus': MENUS,
        'form_data': {},
    })


@admin_only_required
def employee_edit_view(request, pk):
    """Edit a staff/employee account's profile, password, and per-menu access."""
    employee = get_object_or_404(User, pk=pk, role=User.Role.STAFF)

    if request.method == 'POST':
        employee.email = request.POST.get('email', '').strip()
        employee.first_name = request.POST.get('first_name', '').strip()
        employee.last_name = request.POST.get('last_name', '').strip()
        employee.is_active = request.POST.get('is_active') == 'on'

        menu_access = request.POST.getlist('menu_access')
        employee.menu_access = [m for m in menu_access if m in dict(MENUS)]

        new_password = request.POST.get('password', '')
        if new_password:
            employee.set_password(new_password)

        employee.save()
        return redirect('dashboard:employees')

    return render(request, 'dashboard/employee_form.html', {
        'employee': employee,
        'menus': MENUS,
    })


@admin_only_required
def employee_delete_view(request, pk):
    """Delete a staff/employee account."""
    employee = get_object_or_404(User, pk=pk, role=User.Role.STAFF)
    if request.method == 'POST':
        employee.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('dashboard:employees')
    return redirect('dashboard:employees')
