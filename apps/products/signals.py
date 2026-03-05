from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product


@receiver(post_save, sender=Product)
def check_low_stock(sender, instance, **kwargs):
    """Create notification when product hits low/out of stock."""
    from apps.inventory.models import Notification
    if instance.is_out_of_stock:
        Notification.objects.get_or_create(
            notification_type=Notification.OUT_OF_STOCK,
            related_product=instance,
            is_read=False,
            defaults={'message': f'⚠️ OUT OF STOCK: {instance.name} has 0 units left.'}
        )
    elif instance.is_low_stock:
        Notification.objects.get_or_create(
            notification_type=Notification.LOW_STOCK,
            related_product=instance,
            is_read=False,
            defaults={'message': f'🔔 LOW STOCK: {instance.name} has only {instance.stock_qty} unit(s) left.'}
        )
