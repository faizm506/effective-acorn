from django import forms
from .models import Inquiry
import datetime

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['customer_name', 'email', 'phone', 'travel_date', 'message']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special requests?'}),
        }





