from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('notification/', views.midtrans_webhook, name='notification'),
]
