from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('catalog/', views.product_list, name='product_list'),
    path('catalog/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cara-pesan/', views.how_to_order, name='how_to_order'),
]