from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def notification_list(request):
    """Display notifications without changing their read state on GET."""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
@require_POST
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=['is_read'])
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect('notifications:list')
