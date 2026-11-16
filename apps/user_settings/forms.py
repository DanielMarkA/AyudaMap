from django import forms
from .models import UserSettings


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            'dark_mode',
            'email_notifications',
            'notify_on_new_resources',
            'preferred_category',
            'default_latitude',
            'default_longitude',
            'default_zoom',
        ]
        widgets = {
            'dark_mode': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'dark_mode_toggle'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_on_new_resources': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'preferred_category': forms.Select(attrs={'class': 'form-control'}),
            'default_latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'default_longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'default_zoom': forms.NumberInput(attrs={'class': 'form-control', 'min': 5, 'max': 18}),
        }