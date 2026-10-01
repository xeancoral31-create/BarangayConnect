from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Complaint
from .forms import ComplaintForm, AdminComplaintResponseForm
from accounts.views import admin_required, resident_required
from audit.utils import log_activity
from notifications.utils import create_notification


@login_required
def resident_complaint_list(request):
    complaints = Complaint.objects.filter(resident=request.user).order_by('-created_at')
    return render(request, 'complaints/resident/list.html', {'complaints': complaints})


@login_required
def resident_complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk, resident=request.user)
    return render(request, 'complaints/resident/detail.html', {'complaint': complaint})


@resident_required
def resident_complaint_create(request):
    if request.user.account_status != 'active':
        messages.error(request, 'Your account must be active to submit a complaint.')
        return redirect('complaints:resident_list')
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.resident = request.user
            complaint.save()
            log_activity(request.user, 'Submit Complaint', f'Submitted complaint: {complaint.subject}', request)
            messages.success(request, 'Your complaint has been submitted successfully.')
            return redirect('complaints:resident_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ComplaintForm()
    return render(request, 'complaints/resident/form.html', {'form': form})


# ─── Admin ────────────────────────────────────────────────────────────────────

@admin_required
def admin_complaint_list(request):
    complaints = Complaint.objects.select_related('resident').order_by('-created_at')
    search_q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    if search_q:
        complaints = complaints.filter(
            Q(subject__icontains=search_q) |
            Q(resident__first_name__icontains=search_q) |
            Q(resident__last_name__icontains=search_q)
        )
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if category_filter:
        complaints = complaints.filter(category=category_filter)
    paginator = Paginator(complaints, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'complaints/admin/list.html', {
        'page_obj': page_obj,
        'search_q': search_q,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'status_choices': Complaint.STATUS_CHOICES,
        'category_choices': Complaint.CATEGORY_CHOICES,
    })


@admin_required
def admin_complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        form = AdminComplaintResponseForm(request.POST, instance=complaint)
        if form.is_valid():
            old_status = complaint.status
            updated = form.save(commit=False)
            updated.resolved_by = request.user
            updated.save()
            if old_status != updated.status or updated.admin_response:
                create_notification(
                    recipient=complaint.resident,
                    title='Complaint Update',
                    message=f'Your complaint "{complaint.subject}" status: {updated.get_status_display()}',
                    notification_type='complaint'
                )
            log_activity(request.user, 'Update Complaint', f'Updated complaint #{pk} to {updated.status}', request)
            messages.success(request, 'Complaint updated successfully.')
            return redirect('complaints:admin_detail', pk=pk)
    else:
        form = AdminComplaintResponseForm(instance=complaint)
    return render(request, 'complaints/admin/detail.html', {'complaint': complaint, 'form': form})
