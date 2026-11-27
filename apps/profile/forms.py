from django import forms
from django.contrib.auth.models import User
from apps.locations import ALL_CANONICAL_CITIES, OPTIONAL_CITY_CHOICES, normalize_city
from .models import Profile

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
        }

class ProfileEditForm(forms.ModelForm):
    city = forms.ChoiceField(
        required=False,
        choices=OPTIONAL_CITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Profile
        fields = ['full_name', 'organization', 'is_volunteer', 'bio', 'phone_number', 'city', 'profile_image']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name / display name'}),
            'organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NGO, LGU, or Volunteer Group'}),
            'is_volunteer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about yourself or your organization...'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+63 912 345 6789'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_city = normalize_city(getattr(self.instance, 'city', ''))
        if current_city:
            self.initial['city'] = current_city
            if current_city not in ALL_CANONICAL_CITIES:
                self.fields['city'].choices = [
                    *self.fields['city'].choices,
                    ('Other', [(current_city, current_city)]),
                ]
