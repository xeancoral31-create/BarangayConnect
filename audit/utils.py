from .models import ActivityLog


def log_activity(user, action, description='', request=None):
    """Log a user action to the ActivityLog."""
    ip = None
    if request:
        ip = get_client_ip(request)
    ActivityLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip,
    )


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
