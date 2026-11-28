from django import forms
from apps.locations import REQUIRED_CITY_CHOICES
from .models import Resource


class ResourceForm(forms.ModelForm):
    city = forms.ChoiceField(
        required=True,
        choices=REQUIRED_CITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    services_offered = forms.MultipleChoiceField(
        required=False,
        choices=Resource.SERVICE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'service-checkbox-input'}),
    )

    class Meta:
        model = Resource
        fields = [
            'name',
            'category',
            'status',
            'urgency_level',
            'description',
            'services_offered',
            'supplies_needed',
            'city',
            'location',
            'latitude',
            'longitude',
            'is_24_7',
            'opens_at',
            'closes_at',
            'contact_info',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resource or Safe Haven Name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'urgency_level': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Describe available services, access notes, or safety details...'}),
            'supplies_needed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bottled Water, Rice, First Aid Kits'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street, Barangay, or Landmark'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'is_24_7': forms.CheckboxInput(attrs={'class': 'hours-247-checkbox'}),
            'opens_at': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'type': 'time'}),
            'closes_at': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'type': 'time'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number or email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('is_24_7'):
            cleaned_data['opens_at'] = None
            cleaned_data['closes_at'] = None
        return cleaned_data
