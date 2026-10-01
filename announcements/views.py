from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Announcement
from .forms import AnnouncementForm
from accounts.views import admin_required
from audit.utils import log_activity
from notifications.utils import create_notification
from accounts.models import CustomUser


@login_required
def announcement_list(request):
    """Public list for residents — published only."""
    announcements = Announcement.objects.filter(status='published').order_by('-published_at', '-created_at')
    paginator = Paginator(announcements, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'announcements/list.html', {'page_obj': page_obj})


@login_required
def announcement_detail(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.user.is_resident() and announcement.status != 'published':
        messages.error(request, 'This announcement is not available.')
        return redirect('announcements:list')
    return render(request, 'announcements/detail.html', {'announcement': announcement})


# ─── Admin views ──────────────────────────────────────────────────────────────

@admin_required
def admin_announcement_list(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'announcements/admin/list.html', {'announcements': announcements})


@admin_required
def admin_announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            if announcement.status == 'published':
                announcement.published_at = timezone.now()
                # Notify all active residents
                residents = CustomUser.objects.filter(role='resident', account_status='active')
                for resident in residents:
                    create_notification(
                        recipient=resident,
                        title='New Announcement',
                        message=f'New announcement: {announcement.title}',
                        notification_type='announcement'
                    )
            announcement.save()
            log_activity(request.user, 'Create Announcement', f'Created announcement: {announcement.title}', request)
            messages.success(request, f'Announcement "{announcement.title}" created successfully.')
            return redirect('announcements:admin_list')
    else:
        form = AnnouncementForm()
    return render(request, 'announcements/admin/form.html', {'form': form, 'action': 'Create'})


@admin_required
def admin_announcement_edit(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    old_status = announcement.status
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            ann = form.save(commit=False)
            if ann.status == 'published' and old_status != 'published':
                ann.published_at = timezone.now()
            ann.save()
            log_activity(request.user, 'Edit Announcement', f'Edited announcement: {announcement.title}', request)
            messages.success(request, 'Announcement updated successfully.')
            return redirect('announcements:admin_list')
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'announcements/admin/form.html', {'form': form, 'action': 'Edit', 'announcement': announcement})


@admin_required
def admin_announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        title = announcement.title
        announcement.delete()
        log_activity(request.user, 'Delete Announcement', f'Deleted announcement: {title}', request)
        messages.success(request, f'Announcement "{title}" deleted.')
        return redirect('announcements:admin_list')
    return render(request, 'announcements/admin/confirm_delete.html', {'announcement': announcement})


@admin_required
def admin_announcement_publish(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    announcement.status = 'published'
    announcement.published_at = timezone.now()
    announcement.save()
    residents = CustomUser.objects.filter(role='resident', account_status='active')
    for resident in residents:
        create_notification(
            recipient=resident,
            title='New Announcement',
            message=f'New announcement posted: {announcement.title}',
            notification_type='announcement'
        )
    log_activity(request.user, 'Publish Announcement', f'Published: {announcement.title}', request)
    messages.success(request, f'Announcement "{announcement.title}" published.')
    return redirect('announcements:admin_list')


@admin_required
def admin_announcement_archive(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    announcement.status = 'archived'
    announcement.save()
    log_activity(request.user, 'Archive Announcement', f'Archived: {announcement.title}', request)
    messages.success(request, f'Announcement "{announcement.title}" archived.')
    return redirect('announcements:admin_list')
