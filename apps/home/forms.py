from django import forms
from apps.locations import REQUIRED_CITY_CHOICES
from .models import Resource


class ResourceForm(forms.ModelForm):
    city = forms.ChoiceField(
        required=True,
        choices=REQUIRED_CITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Resource
        fields = [
            'name',
            'category',
            'status',
            'urgency_level',
            'description',
            'supplies_needed',
            'capacity_total',
            'capacity_available',
            'city',
            'location',
            'latitude',
            'longitude',
            'operating_hours',
            'contact_info',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resource or Center Name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'urgency_level': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Describe available services or aid...'}),
            'supplies_needed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bottled Water, Rice, First Aid Kits'}),
            'capacity_total': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'capacity_available': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street, Barangay, or Landmark'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'operating_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 24/7 or 8:00 AM - 5:00 PM'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number or email'}),
        }