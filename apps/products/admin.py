from django.contrib import admin
from .models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'selling_price', 'purchase_price', 'stock_qty', 'low_stock_limit', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'barcode']
    list_editable = ['stock_qty', 'is_active']
