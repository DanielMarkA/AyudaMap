from django import forms
from .models import UserSettings

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ['dark_mode', 'email_notifications', 'notify_on_new_resources']
        widgets = {
            'dark_mode': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'dark_mode_toggle'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_on_new_resources': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
