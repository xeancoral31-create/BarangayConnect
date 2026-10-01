from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('', views.resident_request_list, name='resident_list'),
    path('requests/', views.resident_request_list, name='resident_request_list'),
    path('request/', views.resident_request_create, name='resident_create'),
    path('request/new/', views.resident_request_create, name='resident_request_create'),
    path('<int:pk>/', views.resident_request_detail, name='resident_detail'),
    path('<int:pk>/track/', views.resident_request_detail, name='resident_request_detail'),
    # Admin
    path('admin/', views.admin_request_list, name='admin_list'),
    path('admin/requests/', views.admin_request_list, name='admin_request_list'),
    path('admin/<int:pk>/', views.admin_request_detail, name='admin_detail'),
    path('admin/<int:pk>/review/', views.admin_request_detail, name='admin_request_detail'),
    path('admin/types/', views.admin_type_list, name='admin_type_list'),
    path('admin/types/create/', views.admin_type_create, name='admin_type_create'),
    path('admin/types/<int:pk>/edit/', views.admin_type_edit, name='admin_type_edit'),
]
