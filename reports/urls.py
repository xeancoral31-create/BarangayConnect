from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('export/residents/csv/', views.export_residents_csv, name='export_residents_csv'),
    path('export/requests/csv/', views.export_requests_csv, name='export_requests_csv'),
    path('export/complaints/csv/', views.export_complaints_csv, name='export_complaints_csv'),
    path('export/residents/pdf/', views.export_residents_pdf, name='export_residents_pdf'),
]
