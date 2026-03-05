from django import forms
from .models import Invoice


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer_name', 'customer_phone', 'vehicle_number', 'vehicle_model',
                  'service_charge', 'discount', 'gst_percent', 'payment_method', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Name'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. RJ14 AB 1234'}),
            'vehicle_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Honda Shine 125'}),
            'service_charge': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': '0'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': '0'}),
            'gst_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': '0'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
