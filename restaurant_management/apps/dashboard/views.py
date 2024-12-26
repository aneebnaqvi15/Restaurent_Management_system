from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.orders.models import Order, OrderItem
from apps.inventory.models import MenuItem
from apps.tables.models import Table
from django.db.models import Count, Sum, F, Avg
from django.db.models.functions import ExtractHour
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

@login_required
def dashboard(request):
    today = timezone.now().date()
    thirty_days_ago = timezone.now() - timedelta(days=30)

    # Get counts for dashboard widgets
    active_orders = Order.objects.filter(
        status__in=['in_progress', 'preparing', 'ready']
    ).order_by('-created_at')
    active_orders_count = active_orders.count()
    
    # Get available tables count
    available_tables = Table.objects.filter(status='available').count()
    
    # Get low stock items count
    low_stock_count = MenuItem.objects.filter(
        stock_quantity__lte=F('low_stock_threshold')
    ).count()
    
    # Get today's sales
    today_sales = Order.objects.filter(
        created_at__date=today,
        status='completed'
    ).aggregate(
        count=Count('id'),
        total=Sum('total_amount')
    )

    # Get all tables with their current status
    tables = Table.objects.all().order_by('number')

    # Get sales data for the chart
    sales_data = []
    orders_data = []
    
    for i in range(7):
        day = timezone.now().date() - timedelta(days=6-i)
        day_orders = Order.objects.filter(
            created_at__date=day,
            status='completed'
        ).aggregate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        sales_data.append(float(day_orders['total'] or 0))
        orders_data.append(day_orders['count'] or 0)

    context = {
        'active_orders': active_orders[:5],  # Limit to 5 most recent
        'active_orders_count': active_orders_count,
        'available_tables': available_tables,
        'low_stock_count': low_stock_count,
        'today_sales': today_sales,
        'tables': tables,
        'revenue_data': sales_data,
        'orders_data': orders_data,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def reports_page(request):
    # Get date range for reports
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Get order statistics
    orders = Order.objects.filter(created_at__range=[start_date, end_date])
    total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    orders_by_status = orders.values('status').annotate(count=Count('id'))
    
    context = {
        'total_sales': total_sales,
        'orders_by_status': orders_by_status,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'dashboard/reports.html', context)

@login_required
def sales_data(request):
    # Get sales data for charts
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    daily_sales = Order.objects.filter(
        created_at__range=[start_date, end_date],
        status='completed'
    ).values('created_at__date').annotate(
        total=Sum('total_amount')
    ).order_by('created_at__date')
    
    return JsonResponse(list(daily_sales), safe=False)

@login_required
def orders_page(request):
    # Redirect to the new orders view
    return redirect('orders:order-list')

@login_required
def tables_page(request):
    tables = Table.objects.all()
    context = {
        'tables': tables,
        'total_tables': tables.count(),
        'available_tables': tables.filter(status='available').count(),
        'occupied_tables': tables.filter(status='occupied').count(),
        'reserved_tables': tables.filter(status='reserved').count(),
    }
    return render(request, 'tables/table_list.html', context)

@login_required
def inventory_page(request):
    return redirect('inventory:inventory-list')

@login_required
def reports_page(request):
    # Get date range
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)
    
    # Daily sales and orders for the past week
    daily_stats = Order.objects.filter(
        created_at__range=(start_date, end_date)
    ).values('created_at__date').annotate(
        revenue=Sum('total_amount'),
        orders=Count('id')
    ).order_by('created_at__date')

    # Get today's hourly data for real-time chart
    today = timezone.now().date()
    hourly_stats = Order.objects.filter(
        created_at__date=today
    ).annotate(
        hour=ExtractHour('created_at')
    ).values('hour').annotate(
        revenue=Sum('total_amount'),
        orders=Count('id')
    ).order_by('hour')

    # Format hourly data
    hours = []
    hourly_revenue = []
    hourly_orders = []
    current_hour = timezone.now().hour
    
    for hour in range(current_hour + 1):
        hour_data = next((x for x in hourly_stats if x['hour'] == hour), None)
        hours.append(f'{hour:02d}:00')
        hourly_revenue.append(float(hour_data['revenue'] if hour_data else 0))
        hourly_orders.append(hour_data['orders'] if hour_data else 0)

    # Format weekly data for chart
    dates = []
    revenue_data = []
    orders_data = []
    for stat in daily_stats:
        dates.append(stat['created_at__date'].strftime('%a'))
        revenue_data.append(float(stat['revenue'] or 0))
        orders_data.append(stat['orders'])

    # Top selling items
    top_items = OrderItem.objects.values(
        'menu_item__name'
    ).annotate(
        total_orders=Count('id')
    ).order_by('-total_orders')[:5]

    # Revenue by category
    category_revenue = OrderItem.objects.values(
        'menu_item__category__name'
    ).annotate(
        total_revenue=Sum(F('price_at_time') * F('quantity'))
    ).order_by('-total_revenue')[:5]

    # Performance metrics
    avg_order_value = Order.objects.aggregate(
        avg_value=Avg('total_amount')
    )['avg_value'] or 0

    # Table metrics
    table_metrics = {
        'total_tables': Table.objects.count(),
        'occupied_tables': Table.objects.filter(status='occupied').count(),
        'reservations_today': 0  # TODO: Implement actual reservation system
    }

    # Overall statistics
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    avg_rating = 4.8  # TODO: Implement actual rating system

    context = {
        'dates': dates,
        'revenue_data': revenue_data,
        'orders_data': orders_data,
        'hours': hours,
        'hourly_revenue': hourly_revenue,
        'hourly_orders': hourly_orders,
        'top_items': top_items,
        'category_revenue': category_revenue,
        'avg_order_value': avg_order_value,
        'table_metrics': table_metrics,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_rating': avg_rating,
    }
    
    return render(request, 'dashboard/reports.html', context)

@login_required
def sales_data(request):
    """API endpoint for real-time sales data"""
    today = timezone.now().date()
    hourly_stats = Order.objects.filter(
        created_at__date=today
    ).annotate(
        hour=ExtractHour('created_at')
    ).values('hour').annotate(
        revenue=Sum('total_amount'),
        orders=Count('id')
    ).order_by('hour')

    # Format hourly data
    hours = []
    hourly_revenue = []
    hourly_orders = []
    current_hour = timezone.now().hour
    
    for hour in range(current_hour + 1):
        hour_data = next((x for x in hourly_stats if x['hour'] == hour), None)
        hours.append(f'{hour:02d}:00')
        hourly_revenue.append(float(hour_data['revenue'] if hour_data else 0))
        hourly_orders.append(hour_data['orders'] if hour_data else 0)

    return JsonResponse({
        'hours': hours,
        'hourly_revenue': hourly_revenue,
        'hourly_orders': hourly_orders
    })

@login_required
def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('login')
    return redirect('dashboard:dashboard')