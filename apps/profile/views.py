from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Profile
from .forms import UserEditForm, ProfileEditForm
from apps.home.models import Resource, ResourceStatusLog


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    my_resources = Resource.objects.filter(created_by=request.user).order_by('-created_at')
    my_logs = ResourceStatusLog.objects.filter(updated_by=request.user).select_related('resource')[:10]
    total_confirmations = my_resources.aggregate(total=Sum('confirmations'))['total'] or 0

    if request.method == 'POST':
        u_form = UserEditForm(request.POST, instance=request.user)
        p_form = ProfileEditForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            user = u_form.save()
            profile = p_form.save()
            if profile.full_name and not (user.first_name or user.last_name):
                parts = profile.full_name.strip().split(' ', 1)
                user.first_name = parts[0]
                if len(parts) > 1:
                    user.last_name = parts[1]
                user.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile:profile')
    else:
        u_form = UserEditForm(instance=request.user)
        p_form = ProfileEditForm(instance=profile)

    context = {
        'profile': profile,
        'u_form': u_form,
        'p_form': p_form,
        'my_resources': my_resources,
        'my_resources_count': my_resources.count(),
        'my_logs': my_logs,
        'total_confirmations': total_confirmations,
    }
    return render(request, 'profile/profile.html', context)