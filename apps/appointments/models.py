from django.db import models
from django.conf import settings
from apps.services.models import ServiceType


class Appointment(models.Model):
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    RESCHEDULED = 'RESCHEDULED'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (RESCHEDULED, 'Rescheduled'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    vehicle_number = models.CharField(max_length=20)
    vehicle_model = models.CharField(max_length=100)
    service_type = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True, related_name='appointments')
    
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    
    mechanic = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'MECHANIC'},
        related_name='appointments'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_start']

    def __str__(self):
        return f"{self.customer_name} - {self.vehicle_number} | {self.scheduled_start.strftime('%Y-%m-%d %H:%M')}"
