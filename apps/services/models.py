from django.db import models
import json


class ServiceType(models.Model):
    GENERAL = 'GENERAL'
    FULL = 'FULL'
    CUSTOM = 'CUSTOM'

    TYPE_CHOICES = [
        (GENERAL, 'General Service'),
        (FULL, 'Full Service'),
        (CUSTOM, 'Custom Service'),
    ]

    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=GENERAL)
    checklist_template = models.JSONField(default=list, blank=True)
    base_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"

    def get_checklist(self):
        if isinstance(self.checklist_template, list):
            return self.checklist_template
        return json.loads(self.checklist_template)


class ServiceRecord(models.Model):
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    vehicle_number = models.CharField(max_length=20, db_index=True)
    vehicle_model = models.CharField(max_length=100, blank=True)
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=15, blank=True)
    service_type = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True, related_name='records')
    mechanic = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'role': 'MECHANIC'}, related_name='assigned_services'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    checklist = models.JSONField(default=list, blank=True)  # [{item: str, done: bool}]
    notes = models.TextField(blank=True)
    estimated_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vehicle_number} | {self.customer_name} | {self.status}"
