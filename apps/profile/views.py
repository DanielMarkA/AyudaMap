from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile
from .forms import UserEditForm, ProfileEditForm

@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserEditForm(request.POST, instance=request.user)
        p_form = ProfileEditForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile:profile')
    else:
        u_form = UserEditForm(instance=request.user)
        p_form = ProfileEditForm(instance=profile)

    context = {
        'profile': profile,
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'profile/profile.html', context)

