from django import forms
from .models import ServiceRecord, ServiceType


class ServiceTypeForm(forms.ModelForm):
    class Meta:
        model = ServiceType
        fields = ['name', 'service_type', 'base_charge', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'base_charge': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ServiceRecordForm(forms.ModelForm):
    class Meta:
        model = ServiceRecord
        fields = ['vehicle_number', 'vehicle_model', 'customer_name', 'customer_phone',
                  'service_type', 'mechanic', 'estimated_amount', 'notes']
        widgets = {
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. RJ14AB1234'}),
            'vehicle_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Honda Shine'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'service_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_service_type'}),
            'mechanic': forms.Select(attrs={'class': 'form-select'}),
            'estimated_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ServiceStatusForm(forms.ModelForm):
    class Meta:
        model = ServiceRecord
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
