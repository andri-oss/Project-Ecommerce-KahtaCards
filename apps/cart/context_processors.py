from .models import Cart


def cart_context(request):
    """Make cart item count available in all templates."""
    count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.item_count
        except Cart.DoesNotExist:
            pass
    return {'cart_item_count': count}
