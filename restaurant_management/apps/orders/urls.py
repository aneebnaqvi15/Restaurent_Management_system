# apps/orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Template URLs
    path('', views.OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('create/', views.OrderCreateView.as_view(), name='order-create'),
    path('<int:pk>/update/', views.OrderUpdateView.as_view(), name='order-update'),
]