import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Order, OrderItem, RefundRequest
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

            # Copy cart items → order items (preserve design data)
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_image=item.product.image if item.product.image else None,
                    quantity=item.quantity,
                    price=item.product.price,
                    variant_info=item.design_note or '',
                    design_file=item.design_file if item.design_file else None,
                    design_note=item.design_note or '',
                )

            # Cart items are now owned by the order — clear the cart so it
            # doesn't show a duplicate of an order that's already pending payment.
            cart.items.all().delete()

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
        try:
            payment_method = request.POST.get('payment_method', 'qris')

            order.shipping_fee = shipping_fee
            order.tax          = tax
            order.total        = total
            order.save()

            from apps.payments.models import Payment
            from django.conf import settings
            import midtransclient

            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'method': payment_method,
                    'status': Payment.Status.PENDING,
                    'amount': total,
                }
            )

            if not payment.snap_token:
                snap = midtransclient.Snap(
                    is_production=settings.MIDTRANS_IS_PRODUCTION,
                    server_key=settings.MIDTRANS_SERVER_KEY,
                    client_key=settings.MIDTRANS_CLIENT_KEY
                )
                param = {
                    "transaction_details": {
                        "order_id": order.order_id,
                        "gross_amount": int(total)
                    },
                    "customer_details": {
                        "first_name": order.recipient_name,
                        "phone": order.phone,
                    }
                }
                transaction = snap.create_transaction(param)
                payment.snap_token = transaction['token']
                payment.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept') == 'application/json':
                return JsonResponse({'success': True, 'token': payment.snap_token})
            else:
                return redirect('orders:order_success', order_id=order.order_id)
        except Exception as e:
            import traceback
            traceback.print_exc()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept') == 'application/json':
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            raise e
            # Fallback if not AJAX
            return render(request, 'orders/checkout_payment.html', {
                'order': order,
                'order_items': order.items.all(),
                'shipping_fee': shipping_fee,
                'tax': tax,
                'total': total,
                'step': 2,
                'snap_token': payment.snap_token,
                'midtrans_client_key': settings.MIDTRANS_CLIENT_KEY,
            })

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


@login_required
def order_history(request):
    """View user's order history."""
    orders = Order.objects.filter(user=request.user)
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        orders = orders.filter(created_at__date__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__date__lte=end_date)
        
    orders = orders.order_by('-created_at')
    
    return render(request, 'orders/history.html', {
        'orders': orders,
        'start_date': start_date,
        'end_date': end_date,
    })


@login_required
def order_detail(request, order_id):
    """View details of a specific order."""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = order.items.all()

    try:
        refund_request = order.refund_request
    except RefundRequest.DoesNotExist:
        refund_request = None

    return render(request, 'orders/detail.html', {
        'order': order,
        'order_items': order_items,
        'refund_request': refund_request,
    })


@login_required
def order_cancel(request, order_id):
    """AJAX: customer cancels their own order before it is fulfilled."""
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=400)

    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    if not order.can_customer_cancel():
        return JsonResponse({'success': False, 'error': 'Pesanan ini tidak dapat dibatalkan.'}, status=400)

    data = json.loads(request.body) if request.body else {}

    if order.status == Order.Status.PAID:
        bank_name = data.get('bank_name', '').strip()
        account_number = data.get('account_number', '').strip()
        account_holder_name = data.get('account_holder_name', '').strip()

        if not (bank_name and account_number and account_holder_name):
            return JsonResponse({
                'success': False,
                'error': 'Nama bank, nomor rekening, dan nama pemilik rekening wajib diisi untuk proses refund.',
            }, status=400)

        RefundRequest.objects.update_or_create(
            order=order,
            defaults={
                'bank_name': bank_name,
                'account_number': account_number,
                'account_holder_name': account_holder_name,
                'reason': data.get('reason', '').strip(),
            }
        )

    order.status = Order.Status.CANCELLED
    order.save(update_fields=['status', 'updated_at'])

    return JsonResponse({'success': True})


@login_required
def order_confirm_delivery(request, order_id):
    """AJAX: customer confirms a shipped order has arrived, closing it out as delivered."""
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=400)

    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    if not order.can_customer_confirm_delivery():
        return JsonResponse({'success': False, 'error': 'Pesanan ini tidak dapat diselesaikan.'}, status=400)

    order.status = Order.Status.DELIVERED
    order.save(update_fields=['status', 'updated_at'])

    return JsonResponse({'success': True})
