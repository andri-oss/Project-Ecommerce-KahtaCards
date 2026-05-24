from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from apps.cart.models import Cart


@login_required
def checkout_shipping(request):
    """Step 1: Shipping information & method selection."""
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.select_related('product').all()

    if not items.exists():
        return redirect('cart:cart')

    errors = {}

    if request.method == 'POST':
        shipping_method = request.POST.get('shipping_method', 'delivery')
        recipient_name  = request.POST.get('recipient_name', '').strip()
        phone           = request.POST.get('phone', '').strip()
        province        = request.POST.get('province', '').strip()
        city            = request.POST.get('city', '').strip()
        postal_code     = request.POST.get('postal_code', '').strip()
        address         = request.POST.get('address', '').strip()
        save_address    = request.POST.get('save_address') == 'on'

        # ── Server-side validation ──────────────────────────────
        # recipient_name & phone always required
        if not recipient_name:
            errors['recipient_name'] = 'Nama penerima wajib diisi.'
        if not phone:
            errors['phone'] = 'Nomor telepon wajib diisi.'

        # Address fields only required when delivery
        if shipping_method == 'delivery':
            if not province:
                errors['province'] = 'Provinsi wajib dipilih.'
            if not city:
                errors['city'] = 'Kota wajib dipilih.'
            if not postal_code:
                errors['postal_code'] = 'Kode pos wajib diisi.'
            if not address:
                errors['address'] = 'Alamat lengkap wajib diisi.'

        if not errors:
            order = Order.objects.create(
                user=request.user,
                shipping_method=shipping_method,
                recipient_name=recipient_name,
                phone=phone,
                province=province if shipping_method == 'delivery' else '',
                city=city if shipping_method == 'delivery' else '',
                postal_code=postal_code if shipping_method == 'delivery' else '',
                address=address if shipping_method == 'delivery' else 'Ambil di Toko',
                save_address=save_address,
                subtotal=cart.total,
                total=cart.total,
            )

            # Copy cart items → order items (preserve design_note)
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_image=item.product.image if item.product.image else None,
                    quantity=item.quantity,
                    price=item.product.price,
                    variant_info=item.design_note or '',
                )

            return redirect('orders:checkout_payment', order_id=order.order_id)

    # Pre-fill from user profile
    user = request.user
    prefill = {
        'recipient_name': f"{user.first_name} {user.last_name}".strip() or user.username,
        'phone': getattr(user, 'phone_number', ''),
    }

    return render(request, 'orders/checkout_shipping.html', {
        'cart': cart,
        'items': items,
        'step': 1,
        'prefill': prefill,
        'errors': errors,
        'post': request.POST,
    })


@login_required
def checkout_payment(request, order_id):
    """Step 2: Payment method selection & order confirmation."""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    # Guard: don't re-process a paid/cancelled order
    if order.status != Order.Status.PENDING:
        return redirect('orders:order_success', order_id=order.order_id)

    # ── Calculate totals ──────────────────────────────────────
    SHIPPING_FEE = 25000  # flat rate for delivery
    shipping_fee = SHIPPING_FEE if order.shipping_method == 'delivery' else 0
    tax          = int(order.subtotal * 11 / 100)
    total        = int(order.subtotal) + shipping_fee + tax

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'qris')

        order.shipping_fee = shipping_fee
        order.tax          = tax
        order.total        = total
        # NOTE: simplified — no real Midtrans gateway yet; mark as PAID directly
        order.status       = Order.Status.PAID
        order.save()

        from apps.payments.models import Payment
        from django.utils import timezone
        Payment.objects.get_or_create(
            order=order,
            defaults={
                'method': payment_method,
                'status': Payment.Status.COMPLETED,
                'amount': total,
                'paid_at': timezone.now(),
            }
        )

        # Clear the user's cart after successful checkout
        Cart.objects.filter(user=request.user).delete()

        return redirect('orders:order_success', order_id=order.order_id)

    order_items = order.items.all()

    return render(request, 'orders/checkout_payment.html', {
        'order':        order,
        'order_items':  order_items,
        'shipping_fee': shipping_fee,
        'tax':          tax,
        'total':        total,
        'step': 2,
    })


@login_required
def order_success(request, order_id):
    """Step 3: Order confirmation page."""
    order       = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = order.items.all()

    return render(request, 'orders/order_success.html', {
        'order':       order,
        'order_items': order_items,
        'step': 3,
    })
