import json
from django.db.models import Q, F, Count, Sum, Subquery
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from django.views.decorators.http import require_POST
from .models import Resource, ResourceStatusLog
from .forms import ResourceForm
from apps.profile.models import Profile


def _get_impact_summary(resources):
    totals = resources.aggregate(
        total_centers=Count('id'),
        total_capacity=Sum('capacity_total'),
        available_capacity=Sum('capacity_available'),
        total_confirmations=Sum('confirmations'),
    )
    total_cap = totals['total_capacity'] or 0
    avail_cap = totals['available_capacity'] or 0
    utilized_cap = max(0, total_cap - avail_cap)
    utilization_rate = round((utilized_cap / total_cap) * 100, 1) if total_cap > 0 else 0

    category_map = dict(Resource.CATEGORY_CHOICES)
    category_stats = []
    for row in resources.values('category').annotate(
        count=Count('id'),
        avail=Sum('capacity_available'),
        total=Sum('capacity_total'),
    ).order_by('-count'):
        row_total = row['total'] or 0
        row_avail = row['avail'] or 0
        row_pct = round(((row_total - row_avail) / row_total) * 100) if row_total > 0 else 0
        category_stats.append({
            'code': row['category'],
            'label': category_map.get(row['category'], row['category']),
            'count': row['count'],
            'avail': row_avail,
            'total': row_total,
            'utilized_pct': max(0, min(100, row_pct)),
        })

    return {
        'totals': totals,
        'utilized_cap': utilized_cap,
        'utilization_rate': utilization_rate,
        'category_stats': category_stats,
    }


def home_view(request):
    if not request.user.is_authenticated:
        verified_resources = Resource.objects.filter(is_verified=True)
        summary = _get_impact_summary(verified_resources)
        summary['critical_count'] = verified_resources.filter(urgency_level='CRITICAL').count()
        return render(request, 'home/landing.html', summary)

    query = request.GET.get('q', '').strip()
    selected_status = request.GET.get('status', '').strip()
    selected_urgency = request.GET.get('urgency', '').strip()
    local_volunteers = request.GET.get('local_volunteers', '').strip()

    if 'category' in request.GET:
        selected_category = request.GET.get('category', '').strip()
    else:
        user_pref = getattr(getattr(request.user, 'settings', None), 'preferred_category', '')
        selected_category = user_pref if user_pref and user_pref != 'ALL' else ''

    resources = Resource.objects.filter(is_verified=True).select_related('created_by')

    if query:
        resources = resources.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(supplies_needed__icontains=query)
        )
    if selected_category:
        resources = resources.filter(category=selected_category)
    if selected_status:
        resources = resources.filter(status=selected_status)
    if selected_urgency:
        resources = resources.filter(urgency_level=selected_urgency)
    if local_volunteers:
        local_volunteer_ids = Profile.objects.filter(
            is_volunteer=True,
            city=request.user.profile.city,
        ).values('user')
        resources = resources.filter(created_by__in=Subquery(local_volunteer_ids))

    map_data = []
    for r in resources:
        map_data.append({
            'id': r.id,
            'name': r.name,
            'category': r.get_category_display(),
            'category_code': r.category,
            'status': r.status,
            'status_display': r.get_status_display(),
            'urgency': r.urgency_level,
            'urgency_display': r.get_urgency_level_display(),
            'location': r.location,
            'description': r.description or '',
            'supplies_needed': r.supplies_needed or '',
            'capacity_total': r.capacity_total,
            'capacity_available': r.capacity_available,
            'confirmations': r.confirmations,
            'operating_hours': r.operating_hours,
            'contact_info': r.contact_info,
            'lat': r.latitude or 10.3157,
            'lng': r.longitude or 123.8854,
        })
        
    user_settings = getattr(request.user, 'settings', None) if request.user.is_authenticated else None
    user_map_config = {
        'lat': getattr(user_settings, 'default_latitude', 10.3157),
        'lng': getattr(user_settings, 'default_longitude', 123.8854),
        'zoom': getattr(user_settings, 'default_zoom', 12),
    }

    context = {
        'resources': resources,
        'query': query,
        'selected_category': selected_category,
        'selected_status': selected_status,
        'selected_urgency': selected_urgency,
        'local_volunteers': local_volunteers,
        'categories': Resource.CATEGORY_CHOICES,
        'statuses': Resource.STATUS_CHOICES,
        'urgencies': Resource.URGENCY_CHOICES,
        'map_data_json': json.dumps(map_data),
        'resource_form': ResourceForm(),
        'total_count': resources.count(),
        'critical_count': resources.filter(urgency_level='CRITICAL').count(),
    }
    return render(request, 'home/home.html', context)


@login_required
@require_POST
def add_resource_view(request):
    form = ResourceForm(request.POST)
    if form.is_valid():
        resource = form.save(commit=False)
        resource.created_by = request.user
        resource.is_verified = True
        resource.save()
        ResourceStatusLog.objects.create(
            resource=resource,
            updated_by=request.user,
            action_type='STATUS_UPDATE',
            new_status=resource.status,
            note=f"Initial submission ({resource.get_urgency_display()})",
        )
        messages.success(request, f"Resource '{resource.name}' was successfully added to AyudaMap!")
    else:
        messages.error(request, "Please correct the errors in the form.")
    return redirect('home:home')


@login_required
@require_POST
def confirm_resource_view(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    Resource.objects.filter(id=resource.id).update(confirmations=F('confirmations') + 1)
    ResourceStatusLog.objects.create(
        resource=resource,
        updated_by=request.user,
        action_type='CONFIRM_ACTIVE',
        previous_status=resource.status,
        new_status=resource.status,
        note="Verified active on site",
    )
    messages.success(request, f"Confirmed '{resource.name}' is active!")
    return redirect('home:home')


@login_required
@require_POST
def update_resource_status_view(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    new_status = request.POST.get('status', '').strip()
    valid_statuses = dict(Resource.STATUS_CHOICES)

    if new_status in valid_statuses and new_status != resource.status:
        old_status = resource.status
        resource.status = new_status
        if new_status == 'FULL_CAPACITY':
            resource.capacity_available = 0
        resource.save()

        ResourceStatusLog.objects.create(
            resource=resource,
            updated_by=request.user,
            action_type='STATUS_UPDATE',
            previous_status=old_status,
            new_status=new_status,
            note=f"Updated status to {valid_statuses[new_status]}",
        )
        messages.success(request, f"Updated '{resource.name}' to {valid_statuses[new_status]}.")
    return redirect('home:home')

@login_required
def reports_view(request):
    resources = Resource.objects.filter(is_verified=True)
    summary = _get_impact_summary(resources)

    # Breakdown by urgency
    urgency_map = dict(Resource.URGENCY_CHOICES)
    urgency_stats = []
    for row in resources.values('urgency_level').annotate(count=Count('id')).order_by('-count'):
        urgency_stats.append({
            'code': row['urgency_level'],
            'label': urgency_map.get(row['urgency_level'], row['urgency_level']),
            'count': row['count'],
        })

    critical_resources = resources.filter(urgency_level='CRITICAL').order_by('-updated_at')
    recent_logs = ResourceStatusLog.objects.select_related('resource', 'updated_by')[:15]

    context = {
        **summary,
        'urgency_stats': urgency_stats,
        'critical_resources': critical_resources,
        'recent_logs': recent_logs,
    }
    return render(request, 'home/reports.html', context)