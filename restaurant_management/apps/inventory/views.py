# apps/inventory/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Count, Sum, Q, F
from django.contrib import messages
from django.utils import timezone
from .models import MenuItem, Category
from apps.orders.models import Order, OrderItem
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import MenuItemSerializer, CategorySerializer
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import json

# API Views
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        low_stock_items = self.get_queryset().filter(
            stock_quantity__lte=F('low_stock_threshold')
        )
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        menu_item = self.get_object()
        stock_quantity = request.data.get('stock_quantity')
        if stock_quantity is not None:
            menu_item.stock_quantity = stock_quantity
            menu_item.save()
            return Response(self.get_serializer(menu_item).data)
        return Response(
            {'error': 'Stock quantity is required'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# Template Views
class InventoryListView(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'inventory/inventory_list.html'
    context_object_name = 'menu_items'

    def get_queryset(self):
        return MenuItem.objects.select_related('category').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get total items and their value
        total_items = MenuItem.objects.count()
        total_stock = MenuItem.objects.aggregate(
            total_stock=Sum('stock_quantity'),
            total_value=Sum(F('stock_quantity') * F('price'))
        )
        
        # Get low stock items
        low_stock_items = MenuItem.objects.filter(
            stock_quantity__lte=F('low_stock_threshold')
        ).count()
        
        # Get most ordered items in the last 30 days
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        most_ordered = OrderItem.objects.filter(
            order__created_at__gte=thirty_days_ago,
            order__status='completed'
        ).values('menu_item__name').annotate(
            total_orders=Count('id')
        ).order_by('-total_orders')[:5]

        # Get available and unavailable items count
        available_items = MenuItem.objects.filter(stock_quantity__gt=0).count()
        unavailable_items = MenuItem.objects.filter(stock_quantity=0).count()

        # Add statistics to context
        context.update({
            'total_items': total_items,
            'total_stock': total_stock['total_stock'] or 0,
            'total_stock_value': total_stock['total_value'] or 0,
            'low_stock_count': low_stock_items,
            'most_ordered_items': most_ordered,
            'available_items': available_items,
            'unavailable_items': unavailable_items,
            'categories': Category.objects.annotate(item_count=Count('menu_items')),
        })
        
        return context

class AddMenuItemView(LoginRequiredMixin, CreateView):
    model = MenuItem
    template_name = 'inventory/menuitem_form.html'
    fields = ['name', 'category', 'price', 'stock_quantity']
    success_url = reverse_lazy('inventory:inventory_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Menu item added successfully.')
        return super().form_valid(form)

class EditMenuItemView(LoginRequiredMixin, UpdateView):
    model = MenuItem
    template_name = 'inventory/menuitem_form.html'
    fields = ['name', 'category', 'price', 'stock_quantity']
    success_url = reverse_lazy('inventory:inventory_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Menu item updated successfully.')
        return super().form_valid(form)

class DeleteMenuItemView(LoginRequiredMixin, DeleteView):
    model = MenuItem
    success_url = reverse_lazy('inventory:inventory_list')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Menu item deleted successfully.')
        return super().delete(request, *args, **kwargs)


@csrf_protect
@require_http_methods(["POST"])
@login_required
def create_category(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        if not name:
            return JsonResponse({'success': False, 'error': 'Category name is required'}, status=400)
        
        category = Category.objects.create(name=name)
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)