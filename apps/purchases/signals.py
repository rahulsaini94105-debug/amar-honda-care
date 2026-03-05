from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import PurchaseOrder
from apps.inventory.models import StockLog


@receiver(pre_save, sender=PurchaseOrder)
def update_stock_on_receive(sender, instance, **kwargs):
    """When a PO is marked RECEIVED, increase product stock for each item."""
    if instance.pk:
        old = PurchaseOrder.objects.get(pk=instance.pk)
        if old.status != PurchaseOrder.RECEIVED and instance.status == PurchaseOrder.RECEIVED:
            instance.received_at = timezone.now()
            for item in instance.items.all():
                product = item.product
                stock_before = product.stock_qty
                product.stock_qty += item.quantity
                product.save()
                StockLog.objects.create(
                    product=product,
                    change_type=StockLog.PURCHASE,
                    quantity_change=item.quantity,
                    stock_before=stock_before,
                    stock_after=product.stock_qty,
                    note=f'Purchase: PO-{instance.pk}',
                )
