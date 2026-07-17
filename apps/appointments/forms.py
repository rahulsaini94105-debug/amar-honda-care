from django import forms
from django.utils import timezone
from .models import Appointment
from apps.services.models import ServiceType
from apps.accounts.models import User


class CustomerAppointmentForm(forms.ModelForm):
    # Virtual fields for user-friendly date and slot selections
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().strftime('%Y-%m-%d')
        })
    )
    time_slot = forms.ChoiceField(
        choices=[],  # Will populate dynamically
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Appointment
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'vehicle_number', 'vehicle_model', 'service_type', 'notes'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john@example.com'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +91 9876543210'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. DL3SAY1234'}),
            'vehicle_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Honda Activa 6G'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any specific issues/requirements?'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load active service types
        self.fields['service_type'].queryset = ServiceType.objects.filter(is_active=True)
        # Generate hourly time slots (e.g. 09:00 - 10:00 to 17:00 - 18:00)
        slots = []
        for hour in range(9, 18):
            start_str = f"{hour:02d}:00"
            end_str = f"{(hour+1):02d}:00"
            slots.append((f"{start_str}-{end_str}", f"{start_str} - {end_str}"))
        self.fields['time_slot'].choices = slots


class AdminAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'vehicle_number', 'vehicle_model', 'service_type',
            'scheduled_start', 'scheduled_end', 'mechanic', 'status', 'notes'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_model': forms.TextInput(attrs={'class': 'form-control'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_start': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'scheduled_end': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'mechanic': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mechanic'].queryset = User.objects.filter(role='MECHANIC', is_active=True)
