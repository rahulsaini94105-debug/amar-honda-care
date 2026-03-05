def notifications_processor(request):
    """Injects unread notification count into all templates."""
    if request.user.is_authenticated:
        from apps.inventory.models import Notification
        count = Notification.objects.filter(is_read=False).count()
        notifications = Notification.objects.filter(is_read=False)[:5]
        return {
            'unread_notification_count': count,
            'recent_notifications': notifications,
        }
    return {'unread_notification_count': 0, 'recent_notifications': []}
