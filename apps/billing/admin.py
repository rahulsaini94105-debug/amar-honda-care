from django.contrib import admin
from .models import Invoice, InvoiceItem, SparePart, ServiceBillPart


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ['name', 'default_price', 'is_active']
    list_editable = ['default_price', 'is_active']
    search_fields = ['name']


class ServiceBillPartInline(admin.TabularInline):
    model = ServiceBillPart
    extra = 0
    readonly_fields = ['total_price']
    fields = ['spare_part', 'custom_name', 'unit_price', 'quantity', 'total_price']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer_name', 'vehicle_number', 'grand_total', 'payment_method', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['invoice_number', 'customer_name', 'vehicle_number']
    inlines = [InvoiceItemInline, ServiceBillPartInline]
    readonly_fields = ['invoice_number', 'subtotal', 'gst_amount', 'grand_total', 'created_at']
