from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    path('', views.resident_complaint_list, name='resident_list'),
    path('my-complaints/', views.resident_complaint_list, name='resident_complaint_list'),
    path('submit/', views.resident_complaint_create, name='resident_create'),
    path('new/', views.resident_complaint_create, name='resident_complaint_create'),
    path('<int:pk>/', views.resident_complaint_detail, name='resident_detail'),
    # Admin
    path('admin/', views.admin_complaint_list, name='admin_list'),
    path('admin/all/', views.admin_complaint_list, name='admin_complaint_list'),
    path('admin/<int:pk>/', views.admin_complaint_detail, name='admin_detail'),
    path('admin/<int:pk>/review/', views.admin_complaint_detail, name='admin_complaint_detail'),
]
