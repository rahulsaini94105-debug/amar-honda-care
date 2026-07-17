from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'vehicle_number', 'scheduled_start', 'status', 'mechanic')
    list_filter = ('status', 'mechanic', 'scheduled_start')
    search_fields = ('customer_name', 'customer_phone', 'vehicle_number', 'vehicle_model')
    date_hierarchy = 'scheduled_start'
    ordering = ('-scheduled_start',)
