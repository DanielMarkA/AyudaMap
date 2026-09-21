import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resource
from .forms import ResourceForm

@login_required
def home_view(request):
    query = request.GET.get('q', '').strip()
    selected_status = request.GET.get('status', '').strip()
    
    # Check if user explicitly filtered category, or apply user preference
    if 'category' in request.GET:
        selected_category = request.GET.get('category', '').strip()
    else:
        user_pref = getattr(getattr(request.user, 'settings', None), 'preferred_category', '')
        selected_category = user_pref if user_pref and user_pref != 'ALL' else ''

    resources = Resource.objects.filter(is_verified=True).select_related('created_by')

    if query:
        resources = resources.filter(name__icontains=query) | resources.filter(description__icontains=query) | resources.filter(location__icontains=query)
    if selected_category:
        resources = resources.filter(category=selected_category)
    if selected_status:
        resources = resources.filter(status=selected_status)

    # Prepare JSON data for Leaflet Map pins
    map_data = []
    for r in resources:
        map_data.append({
            'id': r.id,
            'name': r.name,
            'category': r.get_category_display(),
            'category_code': r.category,
            'status': r.status,
            'status_display': r.get_status_display(),
            'location': r.location,
            'description': r.description or '',
            'operating_hours': r.operating_hours,
            'contact_info': r.contact_info,
            'lat': r.latitude or 14.5995,
            'lng': r.longitude or 120.9842,
        })

    resource_form = ResourceForm()

    context = {
        'resources': resources,
        'query': query,
        'selected_category': selected_category,
        'selected_status': selected_status,
        'categories': Resource.CATEGORY_CHOICES,
        'statuses': Resource.STATUS_CHOICES,
        'map_data_json': json.dumps(map_data),
        'resource_form': resource_form,
        'total_count': resources.count(),
    }
    return render(request, 'home/home.html', context)

@login_required
def add_resource_view(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.created_by = request.user
            resource.is_verified = True
            resource.save()
            messages.success(request, f"Resource '{resource.name}' was successfully added to AyudaMap!")
            return redirect('home:home')
        else:
            messages.error(request, "Please correct the errors in the form.")
    return redirect('home:home')