from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.orders.models import Order, OrderItem
from apps.catalog.models import Product, Category
from apps.accounts.models import User
from apps.payments.models import Payment


@staff_member_required(login_url='/auth/login/')
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
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

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


@staff_member_required(login_url='/auth/login/')
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


@staff_member_required(login_url='/auth/login/')
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


@staff_member_required(login_url='/auth/login/')
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


@staff_member_required(login_url='/auth/login/')
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


@staff_member_required(login_url='/auth/login/')
def product_delete_view(request, pk):
    """Delete a product."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('dashboard:products')
    return redirect('dashboard:products')


@staff_member_required(login_url='/auth/login/')
def orders_view(request):
    """Order management list with filters."""
    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '')

    orders = Order.objects.select_related('user').order_by('-created_at')

    if status_filter:
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
    }

    return render(request, 'dashboard/orders.html', {
        'page_obj': page,
        'status_filter': status_filter,
        'search': search,
        'summary': summary,
    })


@staff_member_required(login_url='/auth/login/')
def order_detail_view(request, pk):
    """Single order detail with update capability."""
    order = get_object_or_404(Order.objects.select_related('user'), pk=pk)
    items = order.items.select_related('product').all()

    try:
        payment = order.payment
    except Payment.DoesNotExist:
        payment = None

    return render(request, 'dashboard/order_detail.html', {
        'order': order,
        'items': items,
        'payment': payment,
    })


@staff_member_required(login_url='/auth/login/')
def order_update_status(request, pk):
    """AJAX: update order status."""
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk)
        import json
        data = json.loads(request.body)
        new_status = data.get('status')
        if new_status in dict(Order.Status.choices):
            order.status = new_status
            order.save(update_fields=['status', 'updated_at'])
            return JsonResponse({
                'success': True,
                'status': order.status,
                'status_display': order.get_status_display()
            })
    return JsonResponse({'success': False}, status=400)


@staff_member_required(login_url='/auth/login/')
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
