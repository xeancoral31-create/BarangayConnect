from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import ActivityLog
from accounts.views import admin_required


@admin_required
def activity_log_list(request):
    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')
    action_filter = request.GET.get('action', '')
    if action_filter:
        logs = logs.filter(action__icontains=action_filter)
    paginator = Paginator(logs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'audit/log_list.html', {
        'page_obj': page_obj,
        'action_filter': action_filter,
    })
