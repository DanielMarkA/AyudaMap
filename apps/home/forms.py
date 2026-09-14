from django import forms
from .models import Resource

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['name', 'category', 'description', 'location', 'latitude', 'longitude', 'operating_hours', 'contact_info']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resource or Center Name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe available services or aid...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address or Landmark'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'operating_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 24/7 or 8:00 AM - 5:00 PM'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number or email'}),
        }

