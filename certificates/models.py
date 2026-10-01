from django.db import models
from django.conf import settings


class CertificateType(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    requirements = models.TextField(blank=True, help_text='List of required documents')
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    processing_days = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CertificateRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('ready', 'Ready for Release'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificate_requests')
    certificate_type = models.ForeignKey(CertificateType, on_delete=models.PROTECT)
    purpose = models.CharField(max_length=255)
    copies = models.PositiveIntegerField(default=1)
    additional_info = models.TextField(blank=True)
    preferred_release_date = models.DateField(null=True, blank=True)
    supporting_document = models.FileField(upload_to='certificate_docs/', null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True, help_text='Admin remarks')
    approved_document = models.FileField(upload_to='approved_certs/', null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_certificates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.resident.get_full_name()} — {self.certificate_type.name} ({self.status})"

    @property
    def status_badge_class(self):
        mapping = {
            'pending': 'warning',
            'under_review': 'info',
            'approved': 'primary',
            'ready': 'success',
            'completed': 'secondary',
            'rejected': 'danger',
        }
        return mapping.get(self.status, 'secondary')
