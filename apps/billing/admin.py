from django.contrib import admin
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer_name', 'vehicle_number', 'grand_total', 'payment_method', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['invoice_number', 'customer_name', 'vehicle_number']
    inlines = [InvoiceItemInline]
    readonly_fields = ['invoice_number', 'subtotal', 'gst_amount', 'grand_total', 'created_at']
