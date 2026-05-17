from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from apps.cart.models import Cart


@login_required
def checkout_shipping(request):
    """Step 1: Shipping information."""
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.select_related('product').all()

    if not items.exists():
        return redirect('cart:cart')

    if request.method == 'POST':
        # Save order with shipping info, redirect to payment
        order = Order.objects.create(
            user=request.user,
            shipping_method=request.POST.get('shipping_method', 'delivery'),
            recipient_name=request.POST.get('recipient_name', ''),
            phone=request.POST.get('phone', ''),
            province=request.POST.get('province', ''),
            city=request.POST.get('city', ''),
            postal_code=request.POST.get('postal_code', ''),
            address=request.POST.get('address', ''),
            save_address=request.POST.get('save_address') == 'on',
            subtotal=cart.total,
            total=cart.total,  # shipping calculated later
        )

        # Copy cart items to order items
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_image=item.product.image if item.product.image else None,
                quantity=item.quantity,
                price=item.product.price,
            )

        return redirect('orders:checkout_payment', order_id=order.order_id)

    return render(request, 'orders/checkout_shipping.html', {
        'cart': cart,
        'items': items,
        'step': 1,
    })


@login_required
def checkout_payment(request, order_id):
    """Step 2: Payment method selection."""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'qris')

        # Calculate totals
        shipping_fee = 125000 if order.shipping_method == 'delivery' else 0
        tax = int(order.subtotal * 11 / 100)
        total = order.subtotal + shipping_fee + tax

        order.shipping_fee = shipping_fee
        order.tax = tax
        order.total = total
        order.status = Order.Status.PAID  # simplified — no real payment gateway
        order.save()

        # Create payment record
        from apps.payments.models import Payment
        from django.utils import timezone
        Payment.objects.create(
            order=order,
            method=payment_method,
            status=Payment.Status.COMPLETED,
            amount=total,
            paid_at=timezone.now(),
        )

        # Clear cart
        Cart.objects.filter(user=request.user).delete()

        return redirect('orders:order_success', order_id=order.order_id)

    order_items = order.items.all()

    return render(request, 'orders/checkout_payment.html', {
        'order': order,
        'order_items': order_items,
        'step': 2,
    })


@login_required
def order_success(request, order_id):
    """Step 3: Order confirmation."""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = order.items.all()

    return render(request, 'orders/order_success.html', {
        'order': order,
        'order_items': order_items,
        'step': 3,
    })
