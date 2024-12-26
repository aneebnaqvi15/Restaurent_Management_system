# apps/orders/models.py
from django.db import models
from django.core.validators import MinValueValidator

class Order(models.Model):
    ORDER_STATUS = (
        ('in_progress', 'In Progress'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    order_number = models.CharField(max_length=10, unique=True)
    table = models.ForeignKey('tables.Table', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='in_progress')
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_number} - {self.status}"

    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey('inventory.MenuItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} in Order #{self.order.order_number}"