from django import forms
from .models import Complaint


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject', 'description', 'category', 'location', 'incident_date', 'supporting_document', 'contact_preference']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief subject of your complaint'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed description of the complaint or concern'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location of incident (optional)'}),
            'incident_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supporting_document': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,.pdf'}),
            'contact_preference': forms.Select(attrs={'class': 'form-select'}),
        }


class AdminComplaintResponseForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status', 'admin_response', 'resolution']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_response': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Response to the complainant'}),
            'resolution': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Resolution details and actions taken'}),
        }
