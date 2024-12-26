from rest_framework import serializers
from .models import MenuItem, Order, OrderItem

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'description', 'is_available']

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'price_at_time']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'table_number', 'status', 'total_amount', 'items', 'created_at']