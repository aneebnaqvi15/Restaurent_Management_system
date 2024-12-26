# apps/tables/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Table, Reservation
from .serializers import TableSerializer, ReservationSerializer
from datetime import datetime

# API Views
class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        table = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Table.STATUS_CHOICES):
            table.status = new_status
            table.save()
            return Response(self.get_serializer(table).data)
        return Response(
            {'error': 'Invalid status'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


@api_view(['POST'])
def create_reservation(request):
    try:
        data = request.data
        table = Table.objects.get(id=data['table'])
        
        # Convert string date and time to datetime
        date_str = data['reservation_date']
        time_str = data['reservation_time']
        reservation_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

        # Create the reservation
        reservation = Reservation.objects.create(
            table=table,
            customer_name=data['customer_name'],
            customer_phone=data['customer_phone'],
            guest_count=data['guest_count'],
            reservation_date=date_str,
            reservation_time=time_str
        )

        # Update table status
        table.status = 'reserved'
        table.reservation_time = reservation_datetime
        table.save()

        return Response({'message': 'Reservation created successfully'}, status=status.HTTP_201_CREATED)
    except Table.DoesNotExist:
        return Response({'error': 'Table not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Template Views
class TableListView(LoginRequiredMixin, ListView):
    model = Table
    template_name = 'tables/table_list.html'
    context_object_name = 'tables'

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add table statistics
        context['stats'] = {
            'total_tables': Table.objects.count(),
            'available_tables': Table.objects.filter(status='available').count(),
            'occupied_tables': Table.objects.filter(status='occupied').count(),
            'reserved_tables': Table.objects.filter(status='reserved').count(),
        }
        
        # Add status choices for filter
        context['table_statuses'] = Table.STATUS_CHOICES
        return context


class TableCreateView(LoginRequiredMixin, CreateView):
    model = Table
    template_name = 'tables/table_form.html'
    fields = ['number', 'capacity', 'status']
    success_url = reverse_lazy('tables:table-list')


class TableUpdateView(LoginRequiredMixin, UpdateView):
    model = Table
    template_name = 'tables/table_form.html'
    fields = ['status']
    success_url = reverse_lazy('tables:table-list')  # Updated with correct namespace


class TableDeleteView(LoginRequiredMixin, DeleteView):
    model = Table
    template_name = 'tables/table_confirm_delete.html'
    success_url = reverse_lazy('tables:table-list')


class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    template_name = 'tables/reservation_form.html'
    fields = [
        'table',
        'customer_name',
        'customer_phone',
        'guest_count',
        'reservation_date',
        'reservation_time'
    ]
    success_url = reverse_lazy('tables:table-list')


@login_required
def reservation_form(request):
    if request.method == 'POST':
        try:
            table = Table.objects.get(id=request.POST.get('table'))
            
            # Convert string date and time to datetime
            date_str = request.POST.get('reservation_date')
            time_str = request.POST.get('reservation_time')
            reservation_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

            # Create the reservation
            reservation = Reservation.objects.create(
                table=table,
                customer_name=request.POST.get('customer_name'),
                customer_phone=request.POST.get('customer_phone'),
                guest_count=request.POST.get('guest_count'),
                reservation_date=date_str,
                reservation_time=time_str
            )

            # Update table status
            table.status = 'reserved'
            table.reservation_time = reservation_datetime
            table.save()

            messages.success(request, 'Reservation created successfully!')
            return redirect('/')
        except Exception as e:
            messages.error(request, f'Error creating reservation: {str(e)}')
    
    # Get available tables for the form
    available_tables = Table.objects.filter(status='available')
    
    context = {
        'tables': available_tables,
        'min_date': datetime.now().strftime('%Y-%m-%d')
    }
    return render(request, 'tables/reservation_form.html', context)
