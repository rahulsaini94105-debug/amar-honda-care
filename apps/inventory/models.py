from django.db import models
from apps.products.models import Product


class StockLog(models.Model):
    SALE = 'SALE'
    PURCHASE = 'PURCHASE'
    ADJUSTMENT = 'ADJUSTMENT'
    RETURN = 'RETURN'

    CHANGE_TYPE_CHOICES = [
        (SALE, 'Sale'),
        (PURCHASE, 'Purchase'),
        (ADJUSTMENT, 'Adjustment'),
        (RETURN, 'Return'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_logs')
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE_CHOICES)
    quantity_change = models.IntegerField()  # negative for sales/returns, positive for purchases
    stock_before = models.IntegerField()
    stock_after = models.IntegerField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} | {self.change_type} | {self.quantity_change}"


class Notification(models.Model):
    LOW_STOCK = 'LOW_STOCK'
    OUT_OF_STOCK = 'OUT_OF_STOCK'
    SERVICE = 'SERVICE'
    GENERAL = 'GENERAL'

    NOTIFICATION_TYPE_CHOICES = [
        (LOW_STOCK, 'Low Stock'),
        (OUT_OF_STOCK, 'Out of Stock'),
        (SERVICE, 'Service'),
        (GENERAL, 'General'),
    ]

    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    related_product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.message[:60]}"
