from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import UserSettings
from .forms import UserSettingsForm

@login_required
def settings_view(request):
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
    
    settings_form = UserSettingsForm(instance=user_settings)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        action = request.POST.get('action', 'save_settings')
        
        if action == 'save_settings':
            settings_form = UserSettingsForm(request.POST, instance=user_settings)
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, "Your preferences and settings have been saved successfully!")
                return redirect('user_settings:settings')
        
        elif action == 'change_password':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password has been changed successfully!")
                return redirect('user_settings:settings')
            else:
                messages.error(request, "Please correct the password errors below.")

    context = {
        'settings': user_settings,
        'form': settings_form,
        'password_form': password_form,
    }
    return render(request, 'user_settings/settings.html', context)
