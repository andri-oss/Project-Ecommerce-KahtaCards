from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.core.paginator import Paginator

def home_view(request):
    products = Product.objects.filter(is_active=True)[:6]  # featured

    return render(request, 'catalog/home.html', {
        'products': products
    })
    
def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Price range filter
    max_price = request.GET.get('max_price')
    if max_price and max_price != '10000':
        try:
            products = products.filter(price__lte=int(max_price))
        except (ValueError, TypeError):
            pass

    # Min quantity filter
    min_qty = request.GET.get('min_qty')
    if min_qty:
        try:
            products = products.filter(min_order__lte=int(min_qty))
        except (ValueError, TypeError):
            pass

    # Sort
    sort = request.GET.get('sort', 'newest')
    sort_map = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    paginator = Paginator(products, 6)  # 6 produk per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'catalog/product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_slug
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # Related products from same category
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


def how_to_order(request):
    return render(request, 'catalog/how_to_order.html')