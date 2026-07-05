from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_history, name='order_history'),
    path('detail/<str:order_id>/', views.order_detail, name='order_detail'),
    path('detail/<str:order_id>/cancel/', views.order_cancel, name='order_cancel'),
    path('detail/<str:order_id>/confirm-delivery/', views.order_confirm_delivery, name='order_confirm_delivery'),
    path('checkout/shipping/', views.checkout_shipping, name='checkout_shipping'),
    path('checkout/payment/<str:order_id>/', views.checkout_payment, name='checkout_payment'),
    path('checkout/success/<str:order_id>/', views.order_success, name='order_success'),
    path('payment/finish/', views.payment_finish_redirect, name='payment_finish_redirect'),
]
