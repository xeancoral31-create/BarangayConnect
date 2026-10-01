from django.urls import path
from . import views

app_name = 'announcements'

urlpatterns = [
    path('', views.announcement_list, name='list'),
    path('<int:pk>/', views.announcement_detail, name='detail'),
    # Admin
    path('admin/', views.admin_announcement_list, name='admin_list'),
    path('admin/create/', views.admin_announcement_create, name='admin_create'),
    path('admin/<int:pk>/edit/', views.admin_announcement_edit, name='admin_edit'),
    path('admin/<int:pk>/delete/', views.admin_announcement_delete, name='admin_delete'),
    path('admin/<int:pk>/publish/', views.admin_announcement_publish, name='admin_publish'),
    path('admin/<int:pk>/archive/', views.admin_announcement_archive, name='admin_archive'),
]
