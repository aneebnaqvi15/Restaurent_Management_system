# apps/tables/models.py
from django.db import models

class Reservation(models.Model):
    table = models.ForeignKey('Table', on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    guest_count = models.PositiveIntegerField()
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reservation for {self.customer_name} on {self.reservation_date} at {self.reservation_time}"

class Table(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
    ]
    
    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_active = models.BooleanField(default=True)
    order_number = models.CharField(max_length=50, blank=True, null=True)
    reservation_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Table {self.number} ({self.capacity} seats)"