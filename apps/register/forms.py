from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from apps.locations import OPTIONAL_CITY_CHOICES


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter email address',
            'class': 'form-control',
        })
    )
    full_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your full name (shown on aid pins)',
            'class': 'form-control',
        })
    )
    city = forms.ChoiceField(
        required=False,
        choices=OPTIONAL_CITY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'city']

    def clean_full_name(self):
        value = self.cleaned_data.get('full_name', '').strip()
        if not value:
            raise forms.ValidationError("Please enter your full name.")
        return value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
