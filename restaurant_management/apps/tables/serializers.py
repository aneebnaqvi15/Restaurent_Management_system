# apps/tables/serializers.py
from rest_framework import serializers
from .models import Table, Reservation

class ReservationSerializer(serializers.ModelSerializer):
    table_number = serializers.IntegerField(source='table.number', read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'table', 'table_number', 'customer_name', 
            'customer_phone', 'guest_count', 'reservation_date', 
            'reservation_time', 'created_at'
        ]
        read_only_fields = ['created_at']

class TableSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    current_reservation = serializers.SerializerMethodField()
    
    class Meta:
        model = Table
        fields = [
            'id', 'number', 'capacity', 'status', 
            'status_display', 'is_active', 'current_reservation'
        ]
    
    def get_current_reservation(self, obj):
        from django.utils import timezone
        now = timezone.now()
        current_reservation = obj.reservation_set.filter(
            reservation_date=now.date()
        ).first()
        if current_reservation:
            return ReservationSerializer(current_reservation).data
        return None