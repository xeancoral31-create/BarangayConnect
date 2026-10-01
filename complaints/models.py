from django.db import models
from django.conf import settings


class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ('noise', 'Noise Complaint'),
        ('garbage', 'Garbage / Sanitation'),
        ('road', 'Road / Infrastructure'),
        ('neighbor', 'Neighbor Dispute'),
        ('safety', 'Public Safety'),
        ('flooding', 'Flooding / Drainage'),
        ('illegal', 'Illegal Activities'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ]
    CONTACT_CHOICES = [
        ('phone', 'Phone Call'),
        ('email', 'Email'),
        ('personal', 'Personal Visit'),
        ('none', 'No Preference'),
    ]

    resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints')
    subject = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=255, blank=True)
    incident_date = models.DateField(null=True, blank=True)
    supporting_document = models.FileField(upload_to='complaint_docs/', null=True, blank=True)
    contact_preference = models.CharField(max_length=10, choices=CONTACT_CHOICES, default='none')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='submitted')
    admin_response = models.TextField(blank=True, help_text='Admin response to complainant')
    resolution = models.TextField(blank=True, help_text='Resolution details')
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_complaints'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} — {self.resident.get_full_name()} ({self.status})"

    @property
    def status_badge_class(self):
        mapping = {
            'submitted': 'warning',
            'under_review': 'info',
            'in_progress': 'primary',
            'resolved': 'success',
            'closed': 'secondary',
            'rejected': 'danger',
        }
        return mapping.get(self.status, 'secondary')
