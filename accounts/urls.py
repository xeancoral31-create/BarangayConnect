from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
    # Admin: Residents
    path('admin/residents/', views.admin_residents_list, name='admin_residents_list'),
    path('admin/residents/create/', views.admin_resident_create, name='admin_resident_create'),
    path('admin/residents/<int:pk>/', views.admin_resident_detail, name='admin_resident_detail'),
    path('admin/residents/<int:pk>/edit/', views.admin_resident_edit, name='admin_resident_edit'),
    path('admin/residents/<int:pk>/approve/', views.admin_approve_resident, name='admin_approve_resident'),
    path('admin/residents/<int:pk>/reject/', views.admin_reject_resident, name='admin_reject_resident'),
    path('admin/residents/<int:pk>/deactivate/', views.admin_deactivate_resident, name='admin_deactivate_resident'),
    path('admin/residents/<int:pk>/restore/', views.admin_restore_resident, name='admin_restore_resident'),
    path('admin/residents/<int:pk>/reset-password/', views.admin_reset_password, name='admin_reset_password'),
    # Admin: Officials
    path('admin/officials/', views.admin_officials_list, name='admin_officials_list'),
    path('admin/officials/create/', views.admin_official_create, name='admin_official_create'),
    path('admin/officials/<int:pk>/edit/', views.admin_official_edit, name='admin_official_edit'),
    path('admin/officials/<int:pk>/delete/', views.admin_official_delete, name='admin_official_delete'),
]
