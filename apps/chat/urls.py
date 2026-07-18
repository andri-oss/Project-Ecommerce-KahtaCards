from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.customer_chat_view, name='customer_chat'),
    path('send/', views.customer_chat_send, name='customer_send'),
    path('poll/', views.customer_chat_poll, name='customer_poll'),
    path('unread/', views.customer_unread_count, name='customer_unread'),
]
