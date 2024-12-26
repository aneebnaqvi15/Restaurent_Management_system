# apps/inventory/serializers.py
from rest_framework import serializers
from .models import MenuItem, Category

class CategorySerializer(serializers.ModelSerializer):
    menu_items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'menu_items_count']
    
    def get_menu_items_count(self, obj):
        return obj.menu_items.count()

class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'category', 'category_name', 
                 'description', 'price', 'image', 'is_available', 
                 'stock_quantity', 'low_stock_threshold', 
                 'is_low_stock', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'is_low_stock']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation['image']:
            request = self.context.get('request')
            if request is not None:
                representation['image'] = request.build_absolute_uri(instance.image.url)
        return representation