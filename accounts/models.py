from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('resident', 'Resident'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    CIVIL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('widowed', 'Widowed'),
        ('separated', 'Separated'),
        ('divorced', 'Divorced'),
    ]
    ACCOUNT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('rejected', 'Rejected'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='resident')
    account_status = models.CharField(max_length=10, choices=ACCOUNT_STATUS_CHOICES, default='pending')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    civil_status = models.CharField(max_length=15, choices=CIVIL_STATUS_CHOICES, blank=True)
    address = models.TextField(blank=True)
    barangay = models.CharField(max_length=100, blank=True, default='Barangay San Jose')
    valid_id = models.FileField(upload_to='valid_ids/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    def is_admin(self):
        return self.role == 'admin'

    def is_resident(self):
        return self.role == 'resident'

    def is_active_resident(self):
        return self.role == 'resident' and self.account_status == 'active'

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default_avatar.png'


class BarangayOfficial(models.Model):
    POSITION_CHOICES = [
        ('punong_barangay', 'Punong Barangay'),
        ('kagawad', 'Barangay Kagawad'),
        ('sk_chairman', 'SK Chairman'),
        ('secretary', 'Barangay Secretary'),
        ('treasurer', 'Barangay Treasurer'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=150)
    position = models.CharField(max_length=30, choices=POSITION_CHOICES, default='kagawad')
    position_label = models.CharField(max_length=100, blank=True, help_text='Custom position label')
    photo = models.ImageField(upload_to='officials/', null=True, blank=True)
    contact = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    committee = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} — {self.get_position_display()}"


class SystemSetting(models.Model):
    barangay_name = models.CharField(max_length=150, default='Barangay San Jose')
    municipality = models.CharField(max_length=150, default='Municipality of Sample')
    province = models.CharField(max_length=150, default='Province of Sample')
    address = models.TextField(blank=True)
    contact = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to='system/', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'System Setting'

    def __str__(self):
        return self.barangay_name

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
