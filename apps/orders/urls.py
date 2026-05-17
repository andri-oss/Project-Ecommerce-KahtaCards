from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/shipping/', views.checkout_shipping, name='checkout_shipping'),
    path('checkout/payment/<str:order_id>/', views.checkout_payment, name='checkout_payment'),
    path('checkout/success/<str:order_id>/', views.order_success, name='order_success'),
]
