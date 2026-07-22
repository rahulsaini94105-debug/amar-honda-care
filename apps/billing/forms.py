from django import forms
from .models import Invoice
import re


class InvoiceForm(forms.ModelForm):
    customer_phone = forms.CharField(
        max_length=10, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number', 'maxlength': '10'})
    )
    vehicle_number = forms.CharField(
        max_length=20, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. RJ14 AB 1234'})
    )

    class Meta:
        model = Invoice
        fields = ['customer_name', 'customer_phone', 'customer_address', 'vehicle_number', 'vehicle_model',
                  'service_charge', 'discount', 'gst_percent', 'payment_method', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Name'}),
            'customer_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Address'}),
            'vehicle_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Hero Honda Shine 125'}),
            'service_charge': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': '0'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': '0'}),
            'gst_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': '0'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_customer_phone(self):
        phone = self.cleaned_data.get('customer_phone')
        if phone:
            phone = phone.strip()
            if not phone.isdigit() or len(phone) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def clean_vehicle_number(self):
        val = self.cleaned_data.get('vehicle_number')
        if val:
            val = val.strip()
            pattern = re.compile(r'^[A-Z]{2}[ -]?\d{2}[ -]?[A-Z]{1,2}[ -]?\d{4}$', re.IGNORECASE)
            if not pattern.match(val):
                raise forms.ValidationError("Invalid bike/vehicle number format. E.g., RJ14 AB 1234.")
            return val.upper()
        return val
