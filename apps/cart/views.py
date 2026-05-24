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
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        design_note = data.get('design_note', '').strip()
    else:
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        design_note = request.POST.get('design_note', '').strip()

    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity, 'design_note': design_note}
    )
    if not created:
        item.quantity += quantity
        # Update design note if provided and item didn't have one
        if design_note and not item.design_note:
            item.design_note = design_note
        item.save()

    # Handle file upload if it's multipart
    if request.content_type != 'application/json' and 'design_file' in request.FILES:
        if item.design_file:
            item.design_file.delete(save=False)
        item.design_file = request.FILES['design_file']
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


@login_required
@require_POST
def cart_update_design(request):
    """Update design file and/or design note for a cart item (multipart)."""
    item_id = request.POST.get('item_id')
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    # Update design note
    design_note = request.POST.get('design_note', '').strip()
    item.design_note = design_note

    # Update design file if provided
    if 'design_file' in request.FILES:
        # Delete old file if exists
        if item.design_file:
            item.design_file.delete(save=False)
        item.design_file = request.FILES['design_file']

    # Handle file removal
    if request.POST.get('remove_file') == '1':
        if item.design_file:
            item.design_file.delete(save=False)
            item.design_file = None

    item.save()

    return JsonResponse({
        'success': True,
        'design_note': item.design_note,
        'design_file_name': item.design_file.name.split('/')[-1] if item.design_file else '',
        'has_design': bool(item.design_file or item.design_note),
    })
