from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import InvoiceItem
from apps.inventory.models import StockLog


@receiver(post_save, sender=InvoiceItem)
def reduce_stock_on_sale(sender, instance, created, **kwargs):
    """Reduce product stock when an invoice item is saved (created only)."""
    if created:
        product = instance.product
        stock_before = product.stock_qty
        product.stock_qty = max(0, product.stock_qty - instance.quantity)
        product.save()
        StockLog.objects.create(
            product=product,
            change_type=StockLog.SALE,
            quantity_change=-instance.quantity,
            stock_before=stock_before,
            stock_after=product.stock_qty,
            note=f'Sale: Invoice #{instance.invoice.invoice_number}',
        )
