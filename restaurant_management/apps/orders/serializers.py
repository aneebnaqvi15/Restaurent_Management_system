# apps/orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menu_item', 'menu_item_name', 
                 'quantity', 'price_at_time']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    table_number = serializers.IntegerField(source='table.number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'table', 'table_number', 
                 'status', 'status_display', 'total_amount', 'notes', 
                 'created_at', 'updated_at', 'items']
        read_only_fields = ['order_number', 'created_at', 'updated_at']