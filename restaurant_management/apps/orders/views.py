from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Count, Q, Sum, Avg
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderItem
from apps.inventory.models import MenuItem
from .serializers import OrderSerializer, OrderItemSerializer
import uuid

# API Views
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Order.ORDER_STATUS):
            order.status = new_status
            order.save()
            return Response(self.get_serializer(order).data)
        return Response(
            {'error': 'Invalid status'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        order = self.get_object()
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order=order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


# Template Views
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'order_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = Order.objects.all()
        status_filter = self.request.GET.get('status')
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Get order statistics
        stats = {
            'count': Order.objects.count(),
            'in_progress_count': Order.objects.filter(
                status__in=['in_progress', 'preparing']
            ).count(),
            'completed_today': Order.objects.filter(
                status='completed',
                created_at__date=today
            ).count(),
            'cancelled_count': Order.objects.filter(
                status='cancelled'
            ).count(),
            'total_revenue_today': Order.objects.filter(
                status='completed',
                created_at__date=today
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
            'avg_order_value': Order.objects.filter(
                status='completed'
            ).aggregate(avg=Avg('total_amount'))['avg'] or 0
        }
        
        context['stats'] = stats
        context['status_choices'] = Order.ORDER_STATUS
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    template_name = 'orders/order_form.html'
    fields = ['table', 'notes']
    success_url = reverse_lazy('orders:order-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_items'] = MenuItem.objects.filter(is_available=True)
        return context

    def form_valid(self, form):
        # Generate a unique order number
        form.instance.order_number = str(uuid.uuid4().hex[:6].upper())
        form.instance.status = 'in_progress'
        form.instance.total_amount = 0  # Will be updated after adding items
        
        # Save the order first
        response = super().form_valid(form)
        
        # Process order items
        menu_items = self.request.POST.getlist('menu_items[]')
        quantities = self.request.POST.getlist('quantities[]')
        
        total_amount = 0
        for item_id, quantity in zip(menu_items, quantities):
            menu_item = MenuItem.objects.get(id=item_id)
            quantity = int(quantity)
            price = menu_item.price
            
            OrderItem.objects.create(
                order=self.object,
                menu_item=menu_item,
                quantity=quantity,
                price_at_time=price
            )
            total_amount += price * quantity
        
        # Update order total
        self.object.total_amount = total_amount
        self.object.save()
        
        return response


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    template_name = 'orders/order_form.html'
    fields = ['status', 'notes']
    success_url = reverse_lazy('orders:order-list')