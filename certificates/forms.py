from django import forms
from .models import CertificateType, CertificateRequest


class CertificateRequestForm(forms.ModelForm):
    class Meta:
        model = CertificateRequest
        fields = ['certificate_type', 'purpose', 'copies', 'additional_info', 'preferred_release_date', 'supporting_document']
        widgets = {
            'certificate_type': forms.Select(attrs={'class': 'form-select'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State the purpose of your request'}),
            'copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Additional information (optional)'}),
            'preferred_release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supporting_document': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,.pdf'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['certificate_type'].queryset = CertificateType.objects.filter(is_active=True)


class AdminCertificateStatusForm(forms.ModelForm):
    class Meta:
        model = CertificateRequest
        fields = ['status', 'remarks', 'approved_document']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'approved_document': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,.pdf'}),
        }


class CertificateTypeForm(forms.ModelForm):
    class Meta:
        model = CertificateType
        fields = ['name', 'description', 'requirements', 'fee', 'processing_days', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'processing_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
