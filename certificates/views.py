from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CertificateType, CertificateRequest
from .forms import CertificateRequestForm, AdminCertificateStatusForm, CertificateTypeForm
from accounts.views import admin_required, resident_required
from audit.utils import log_activity
from notifications.utils import create_notification


@login_required
def resident_request_list(request):
    requests = CertificateRequest.objects.filter(resident=request.user).order_by('-created_at')
    return render(request, 'certificates/resident/list.html', {'requests': requests})


@login_required
def resident_request_detail(request, pk):
    cert_request = get_object_or_404(CertificateRequest, pk=pk, resident=request.user)
    return render(request, 'certificates/resident/detail.html', {'cert_request': cert_request})


@resident_required
def resident_request_create(request):
    if request.user.account_status != 'active':
        messages.error(request, 'Your account must be active to submit a certificate request.')
        return redirect('certificates:resident_list')
    if request.method == 'POST':
        form = CertificateRequestForm(request.POST, request.FILES)
        if form.is_valid():
            cert_request = form.save(commit=False)
            cert_request.resident = request.user
            cert_request.save()
            log_activity(request.user, 'Submit Certificate Request', f'Submitted: {cert_request.certificate_type.name}', request)
            messages.success(request, 'Your certificate request has been submitted successfully. Please wait for processing.')
            return redirect('certificates:resident_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CertificateRequestForm()
    return render(request, 'certificates/resident/form.html', {'form': form})


# ─── Admin ───────────────────────────────────────────────────────────────────

@admin_required
def admin_request_list(request):
    requests = CertificateRequest.objects.select_related('resident', 'certificate_type').order_by('-created_at')
    search_q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    if search_q:
        requests = requests.filter(
            Q(resident__first_name__icontains=search_q) |
            Q(resident__last_name__icontains=search_q) |
            Q(resident__username__icontains=search_q) |
            Q(certificate_type__name__icontains=search_q)
        )
    if status_filter:
        requests = requests.filter(status=status_filter)
    if type_filter:
        requests = requests.filter(certificate_type_id=type_filter)
    paginator = Paginator(requests, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    cert_types = CertificateType.objects.all()
    return render(request, 'certificates/admin/list.html', {
        'page_obj': page_obj,
        'search_q': search_q,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'cert_types': cert_types,
        'status_choices': CertificateRequest.STATUS_CHOICES,
    })


@admin_required
def admin_request_detail(request, pk):
    cert_request = get_object_or_404(CertificateRequest, pk=pk)
    if request.method == 'POST':
        form = AdminCertificateStatusForm(request.POST, request.FILES, instance=cert_request)
        if form.is_valid():
            old_status = cert_request.status
            updated = form.save(commit=False)
            updated.processed_by = request.user
            updated.save()
            if old_status != updated.status:
                create_notification(
                    recipient=cert_request.resident,
                    title='Certificate Request Update',
                    message=f'Your request for {cert_request.certificate_type.name} is now: {updated.get_status_display()}',
                    notification_type='certificate'
                )
            log_activity(request.user, 'Update Certificate Request', f'Updated request #{pk} to {updated.status}', request)
            messages.success(request, 'Request updated successfully.')
            return redirect('certificates:admin_detail', pk=pk)
    else:
        form = AdminCertificateStatusForm(instance=cert_request)
    return render(request, 'certificates/admin/detail.html', {'cert_request': cert_request, 'form': form})


# ─── Certificate Types ────────────────────────────────────────────────────────

@admin_required
def admin_type_list(request):
    cert_types = CertificateType.objects.all()
    return render(request, 'certificates/admin/type_list.html', {'cert_types': cert_types})


@admin_required
def admin_type_create(request):
    if request.method == 'POST':
        form = CertificateTypeForm(request.POST)
        if form.is_valid():
            ct = form.save()
            log_activity(request.user, 'Create Certificate Type', f'Created: {ct.name}', request)
            messages.success(request, f'Certificate type "{ct.name}" created.')
            return redirect('certificates:admin_type_list')
    else:
        form = CertificateTypeForm()
    return render(request, 'certificates/admin/type_form.html', {'form': form, 'action': 'Create'})


@admin_required
def admin_type_edit(request, pk):
    ct = get_object_or_404(CertificateType, pk=pk)
    if request.method == 'POST':
        form = CertificateTypeForm(request.POST, instance=ct)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'Edit Certificate Type', f'Edited: {ct.name}', request)
            messages.success(request, f'Certificate type "{ct.name}" updated.')
            return redirect('certificates:admin_type_list')
    else:
        form = CertificateTypeForm(instance=ct)
    return render(request, 'certificates/admin/type_form.html', {'form': form, 'action': 'Edit', 'ct': ct})
