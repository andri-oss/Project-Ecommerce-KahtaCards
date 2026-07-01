from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='index'),
    path('products/', views.products_view, name='products'),
    path('products/add/', views.product_add_view, name='product_add'),
    path('products/<int:pk>/edit/', views.product_edit_view, name='product_edit'),
    path('products/<int:pk>/toggle/', views.product_toggle_view, name='product_toggle'),
    path('products/<int:pk>/delete/', views.product_delete_view, name='product_delete'),
    path('categories/', views.categories_view, name='categories'),
    path('categories/<int:pk>/edit/', views.category_edit_view, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),
    path('orders/', views.orders_view, name='orders'),
    path('orders/<int:pk>/', views.order_detail_view, name='order_detail'),
    path('orders/<int:pk>/update-status/', views.order_update_status, name='order_update_status'),
    path('orders/<int:pk>/refund-completed/', views.refund_mark_completed, name='refund_mark_completed'),
    path('customers/', views.customers_view, name='customers'),
    path('reports/', views.reports_view, name='reports'),
    path('reports/export/', views.reports_export_csv, name='reports_export_csv'),
    path('employees/', views.employees_view, name='employees'),
    path('employees/add/', views.employee_add_view, name='employee_add'),
    path('employees/<int:pk>/edit/', views.employee_edit_view, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete_view, name='employee_delete'),
]
