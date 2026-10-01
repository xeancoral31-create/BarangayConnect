from .models import Notification


def create_notification(recipient, title, message, notification_type='general'):
    """Helper to create a notification for a user."""
    Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
    )
