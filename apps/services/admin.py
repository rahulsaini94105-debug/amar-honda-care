from django.contrib import admin
from .models import ServiceType, ServiceRecord


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'base_charge', 'is_active']
    list_filter = ['service_type', 'is_active']


@admin.register(ServiceRecord)
class ServiceRecordAdmin(admin.ModelAdmin):
    list_display = ['vehicle_number', 'customer_name', 'service_type', 'mechanic', 'status', 'created_at']
    list_filter = ['status', 'service_type']
    search_fields = ['vehicle_number', 'customer_name']
