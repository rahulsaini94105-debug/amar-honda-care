from django.contrib import admin
from .models import StockLog, Notification


@admin.register(StockLog)
class StockLogAdmin(admin.ModelAdmin):
    list_display = ['product', 'change_type', 'quantity_change', 'stock_before', 'stock_after', 'created_at']
    list_filter = ['change_type']
    search_fields = ['product__name']
    readonly_fields = ['created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_type', 'message', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    list_editable = ['is_read']
