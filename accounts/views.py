from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from .models import CustomUser, BarangayOfficial
from .forms import (
    RegistrationForm, LoginForm, ProfileUpdateForm, PasswordChangeForm,
    AdminCreateResidentForm, AdminEditResidentForm, BarangayOfficialForm
)
from audit.utils import log_activity
from notifications.utils import create_notification


def admin_required(view_func):
    """Decorator: requires logged-in admin."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_admin():
            return render(request, 'errors/403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


def resident_required(view_func):
    """Decorator: requires active resident."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_resident():
            return render(request, 'errors/403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            log_activity(None, 'Registration', f'New resident registered: {user.username}', request)
            messages.success(request,
                'Registration successful! Your account is pending approval by the Barangay Administrator.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check account status for residents
            if user.is_resident():
                if user.account_status == 'pending':
                    messages.warning(request, 'Your account is still pending approval. Please wait for administrator verification.')
                    return redirect('accounts:login')
                elif user.account_status in ('inactive', 'rejected'):
                    messages.error(request, 'Your account has been deactivated or rejected. Please contact the Barangay Office.')
                    return redirect('accounts:login')
            login(request, user)
            log_activity(user, 'Login', f'User logged in: {user.username}', request)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    username = request.user.username
    log_activity(request.user, 'Logout', f'User logged out: {username}', request)
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'Profile Update', 'User updated their profile', request)
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            log_activity(request.user, 'Password Change', 'User changed their password', request)
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


# ─── Admin: Resident Management ─────────────────────────────────────────────

@admin_required
def admin_residents_list(request):
    residents = CustomUser.objects.filter(role='resident').order_by('-created_at')
    # Search
    search_q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    if search_q:
        residents = residents.filter(
            Q(username__icontains=search_q) |
            Q(first_name__icontains=search_q) |
            Q(last_name__icontains=search_q) |
            Q(email__icontains=search_q)
        )
    if status_filter:
        residents = residents.filter(account_status=status_filter)
    paginator = Paginator(residents, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'accounts/admin/residents_list.html', {
        'page_obj': page_obj,
        'search_q': search_q,
        'status_filter': status_filter,
    })


@admin_required
def admin_resident_detail(request, pk):
    resident = get_object_or_404(CustomUser, pk=pk, role='resident')
    return render(request, 'accounts/admin/resident_detail.html', {'resident': resident})


@admin_required
def admin_resident_create(request):
    if request.method == 'POST':
        form = AdminCreateResidentForm(request.POST)
        if form.is_valid():
            resident = form.save()
            log_activity(request.user, 'Create Resident', f'Created resident: {resident.username}', request)
            messages.success(request, f'Resident account for {resident.get_full_name()} created successfully.')
            return redirect('accounts:admin_residents_list')
    else:
        form = AdminCreateResidentForm()
    return render(request, 'accounts/admin/resident_form.html', {'form': form, 'action': 'Create'})


@admin_required
def admin_resident_edit(request, pk):
    resident = get_object_or_404(CustomUser, pk=pk, role='resident')
    if request.method == 'POST':
        form = AdminEditResidentForm(request.POST, instance=resident)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'Edit Resident', f'Edited resident: {resident.username}', request)
            messages.success(request, f'Resident {resident.get_full_name()} updated successfully.')
            return redirect('accounts:admin_resident_detail', pk=pk)
    else:
        form = AdminEditResidentForm(instance=resident)
    return render(request, 'accounts/admin/resident_form.html', {'form': form, 'action': 'Edit', 'resident': resident})


@admin_required
def admin_approve_resident(request, pk):
    resident = get_object_or_404(CustomUser, pk=pk, role='resident')
    resident.account_status = 'active'
    resident.is_active = True
    resident.save()
    create_notification(
        recipient=resident,
        title='Account Approved',
        message='Your BarangayConnect account has been approved! You can now log in and access all services.',
        notification_type='account'
    )
    log_activity(request.user, 'Approve Resident', f'Approved resident: {resident.username}', request)
    messages.success(request, f'Resident account for {resident.get_full_name()} has been approved.')
    return redirect(request.META.get('HTTP_REFERER', 'accounts:admin_residents_list'))


@admin_required
def admin_reject_resident(request, pk):
    resident = get_object_or_404(CustomUser, pk=pk, role='resident')
    resident.account_status = 'rejected'
    resident.is_active = False
    resident.save()
    create_notification(
        recipient=resident,
        title='Account Rejected',
        message='Your BarangayConnect account registration has been rejected. Please contact the Barangay Office for more information.',
        notification_type='account'
    )
    log_activity(request.user, 'Reject Resident', f'Rejected resident: {resident.username}', request)
    messages.warning(request, f'Resident account for {resident.get_full_name()} has been rejected.')
    return redirect(request.META.get('HTTP_REFERER', 'accounts:admin_residents_list'))


@admin_required
def admin_deactivate_resident(request, pk):
    resident = get_object_or_404(CustomUser, pk=pk, role='resident')
    resident.account_status = 'inactive'
    resident.is_active = False
    resident.save()
    log_activity(request.user, 'Deactivate Resident', f'Deactivated resident: {resident.username}', request)
    messages.warning(request, f'Resident account for {resident.get_full_name()} has been deactivated.')
    return redirect(request.META.get('HTTP_REFERER', 'accounts:admin_residents_list'))


@admin_required
def admin_restore_resident(request, pk):
    resident = get_object_or_404(CustomUser, pk=pk, role='resident')
    resident.account_status = 'active'
    resident.is_active = True
    resident.save()
    create_notification(
        recipient=resident,
        title='Account Restored',
        message='Your BarangayConnect account has been restored. You can log in again.',
        notification_type='account'
    )
    log_activity(request.user, 'Restore Resident', f'Restored resident: {resident.username}', request)
    messages.success(request, f'Resident account for {resident.get_full_name()} has been restored.')
    return redirect(request.META.get('HTTP_REFERER', 'accounts:admin_residents_list'))


@admin_required
def admin_reset_password(request, pk):
    resident = get_object_or_404(CustomUser, pk=pk, role='resident')
    if request.method == 'POST':
        new_password = request.POST.get('new_password', 'BarangayConnect@2024')
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return redirect('accounts:admin_resident_detail', pk=pk)
        resident.set_password(new_password)
        resident.save()
        log_activity(request.user, 'Reset Password', f'Reset password for: {resident.username}', request)
        messages.success(request, f'Password for {resident.get_full_name()} has been reset.')
        return redirect('accounts:admin_resident_detail', pk=pk)
    return render(request, 'accounts/admin/reset_password.html', {'resident': resident})


# ─── Admin: Barangay Officials ───────────────────────────────────────────────

@admin_required
def admin_officials_list(request):
    officials = BarangayOfficial.objects.all()
    return render(request, 'accounts/admin/officials_list.html', {'officials': officials})


@admin_required
def admin_official_create(request):
    if request.method == 'POST':
        form = BarangayOfficialForm(request.POST, request.FILES)
        if form.is_valid():
            official = form.save()
            log_activity(request.user, 'Create Official', f'Added official: {official.name}', request)
            messages.success(request, f'Official {official.name} added successfully.')
            return redirect('accounts:admin_officials_list')
    else:
        form = BarangayOfficialForm()
    return render(request, 'accounts/admin/official_form.html', {'form': form, 'action': 'Add'})


@admin_required
def admin_official_edit(request, pk):
    official = get_object_or_404(BarangayOfficial, pk=pk)
    if request.method == 'POST':
        form = BarangayOfficialForm(request.POST, request.FILES, instance=official)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'Edit Official', f'Edited official: {official.name}', request)
            messages.success(request, f'Official {official.name} updated.')
            return redirect('accounts:admin_officials_list')
    else:
        form = BarangayOfficialForm(instance=official)
    return render(request, 'accounts/admin/official_form.html', {'form': form, 'action': 'Edit', 'official': official})


@admin_required
def admin_official_delete(request, pk):
    official = get_object_or_404(BarangayOfficial, pk=pk)
    if request.method == 'POST':
        name = official.name
        official.delete()
        log_activity(request.user, 'Delete Official', f'Deleted official: {name}', request)
        messages.success(request, f'Official {name} removed.')
        return redirect('accounts:admin_officials_list')
    return render(request, 'accounts/admin/official_confirm_delete.html', {'official': official})


# ─── Error Handlers ──────────────────────────────────────────────────────────

def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
