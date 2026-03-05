from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseItem


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'is_active']
    search_fields = ['name', 'phone']


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'supplier', 'status', 'total_amount', 'created_at']
    list_filter = ['status']
    inlines = [PurchaseItemInline]
