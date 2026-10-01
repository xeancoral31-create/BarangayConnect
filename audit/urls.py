from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.activity_log_list, name='log_list'),
    path('logs/', views.activity_log_list, name='log_list_alt'),
]
