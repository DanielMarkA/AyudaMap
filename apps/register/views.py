from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegisterForm
from apps.profile.models import Profile
from apps.user_settings.models import UserSettings

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home:home")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            full_name = form.cleaned_data.get('full_name', '').strip()

            if full_name:
                name_parts = full_name.split(' ', 1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]

            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            if full_name:
                profile.full_name = full_name
                profile.save()

            UserSettings.objects.get_or_create(user=user)

            login(request, user)
            messages.success(request, f"Welcome to AyudaMap, {user.username}! Your account has been created.")
            return redirect("home:home")
        else:
            return render(request, "register/register.html", {"form": form})
    else:
        form = UserRegisterForm()

    return render(request, "register/register.html", {"form": form})