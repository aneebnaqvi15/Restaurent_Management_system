# apps/inventory/urls.py
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.InventoryListView.as_view(), name='inventory_list'),
    path('menu-items/add/', views.AddMenuItemView.as_view(), name='add_menu_item'),
    path('menu-items/<int:pk>/edit/', views.EditMenuItemView.as_view(), name='edit_menu_item'),
    path('menu-items/<int:pk>/delete/', views.DeleteMenuItemView.as_view(), name='delete_menu_item'),
    path('categories/create/', views.create_category, name='create_category'),
]