from django.contrib import admin
from .models import Table, Reservation

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'status')
    search_fields = ('number',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('table', 'customer_name', 'reservation_time')
    search_fields = ('customer_name',)
