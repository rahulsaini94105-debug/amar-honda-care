from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product


@receiver(post_save, sender=Product)
def check_low_stock(sender, instance, **kwargs):
    """Create, update, or resolve notifications when product hits low/out of stock or goes back in stock."""
    from apps.inventory.models import Notification
    
    if instance.is_out_of_stock:
        # Mark low stock notifications for this product as read
        Notification.objects.filter(
            notification_type=Notification.LOW_STOCK,
            related_product=instance,
            is_read=False
        ).update(is_read=True)
        
        Notification.objects.get_or_create(
            notification_type=Notification.OUT_OF_STOCK,
            related_product=instance,
            is_read=False,
            defaults={'message': f'⚠️ OUT OF STOCK: {instance.name} has 0 units left.'}
        )
    elif instance.is_low_stock:
        # Mark out of stock notifications for this product as read
        Notification.objects.filter(
            notification_type=Notification.OUT_OF_STOCK,
            related_product=instance,
            is_read=False
        ).update(is_read=True)
        
        # Get or create LOW_STOCK notification, updating the message if it already exists
        notif, created = Notification.objects.get_or_create(
            notification_type=Notification.LOW_STOCK,
            related_product=instance,
            is_read=False,
            defaults={'message': f'🔔 LOW STOCK: {instance.name} has only {instance.stock_qty} unit(s) left.'}
        )
        if not created:
            new_message = f'🔔 LOW STOCK: {instance.name} has only {instance.stock_qty} unit(s) left.'
            if notif.message != new_message:
                notif.message = new_message
                notif.save(update_fields=['message'])
    else:
        # Product is back in stock and not low stock. Mark all low stock and out of stock alerts as read.
        Notification.objects.filter(
            notification_type__in=[Notification.LOW_STOCK, Notification.OUT_OF_STOCK],
            related_product=instance,
            is_read=False
        ).update(is_read=True)
