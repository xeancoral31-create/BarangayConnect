from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from announcements.models import Announcement
from certificates.models import CertificateRequest
from complaints.models import Complaint
from notifications.models import Notification
from accounts.views import admin_required, resident_required


@login_required
def index(request):
    """Route users to appropriate dashboard."""
    if request.user.is_admin():
        return redirect('dashboard:admin_dashboard')
    return redirect('dashboard:resident_dashboard')


@admin_required
def admin_dashboard(request):
    total_residents = CustomUser.objects.filter(role='resident').count()
    pending_residents = CustomUser.objects.filter(role='resident', account_status='pending').count()
    pending_requests = CertificateRequest.objects.filter(status='pending').count()
    approved_requests = CertificateRequest.objects.filter(status='approved').count()
    open_complaints = Complaint.objects.filter(status__in=['submitted', 'under_review', 'in_progress']).count()
    total_announcements = Announcement.objects.filter(status='published').count()

    recent_requests = CertificateRequest.objects.select_related('resident', 'certificate_type').order_by('-created_at')[:8]
    recent_complaints = Complaint.objects.select_related('resident').order_by('-created_at')[:8]
    latest_residents = CustomUser.objects.filter(role='resident').order_by('-created_at')[:5]
    recent_announcements = Announcement.objects.order_by('-created_at')[:5]

    context = {
        'total_residents': total_residents,
        'pending_residents': pending_residents,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'open_complaints': open_complaints,
        'total_announcements': total_announcements,
        'recent_requests': recent_requests,
        'recent_complaints': recent_complaints,
        'latest_residents': latest_residents,
        'recent_announcements': recent_announcements,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@resident_required
def resident_dashboard(request):
    my_requests = CertificateRequest.objects.filter(resident=request.user)
    pending_requests = my_requests.filter(status='pending').count()
    approved_requests = my_requests.filter(status__in=['approved', 'ready', 'completed']).count()
    rejected_requests = my_requests.filter(status='rejected').count()
    recent_requests = my_requests.order_by('-created_at')[:5]

    my_complaints = Complaint.objects.filter(resident=request.user)
    open_complaints = my_complaints.filter(status__in=['submitted', 'under_review', 'in_progress']).count()
    recent_complaints = my_complaints.order_by('-created_at')[:3]

    recent_announcements = Announcement.objects.filter(status='published').order_by('-published_at')[:3]
    recent_notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    context = {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'open_complaints': open_complaints,
        'recent_requests': recent_requests,
        'recent_complaints': recent_complaints,
        'recent_announcements': recent_announcements,
        'recent_notifications': recent_notifications,
    }
    return render(request, 'dashboard/resident_dashboard.html', context)
