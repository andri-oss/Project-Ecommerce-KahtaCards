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

    category_slug = request.GET.get('category')

    if category_slug:
        products = products.filter(category__slug=category_slug)

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

    return render(request, 'catalog/product_detail.html', {
        'product': product
    })


def how_to_order(request):
    return render(request, 'catalog/how_to_order.html')