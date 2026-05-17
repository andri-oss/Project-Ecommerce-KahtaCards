from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from apps.catalog.models import Product
import json


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()

    return render(request, 'cart/cart.html', {
        'cart': cart,
        'items': items,
    })


@login_required
@require_POST
def cart_add(request):
    """Add a product to cart (AJAX)."""
    data = json.loads(request.body)
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))

    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()

    return JsonResponse({
        'success': True,
        'item_count': cart.item_count,
        'message': f'{product.name} ditambahkan ke keranjang'
    })


@login_required
@require_POST
def cart_update(request):
    """Update item quantity (AJAX)."""
    data = json.loads(request.body)
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 1))

    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if quantity <= 0:
        item.delete()
    else:
        item.quantity = quantity
        item.save()

    cart = item.cart if quantity > 0 else Cart.objects.get(user=request.user)

    return JsonResponse({
        'success': True,
        'subtotal': int(item.subtotal) if quantity > 0 else 0,
        'total': int(cart.total),
        'item_count': cart.item_count,
    })


@login_required
@require_POST
def cart_remove(request):
    """Remove item from cart (AJAX)."""
    data = json.loads(request.body)
    item_id = data.get('item_id')

    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = item.cart
    item.delete()

    return JsonResponse({
        'success': True,
        'total': int(cart.total),
        'item_count': cart.item_count,
    })
