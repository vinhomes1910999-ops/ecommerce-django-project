from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('success/<str:order_code>/', views.order_success_view, name='order_success'),
    path('history/', views.order_history_view, name='order_history'),
    path('<str:order_code>/', views.order_detail_view, name='order_detail'),
]