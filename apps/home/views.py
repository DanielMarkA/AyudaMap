import json
from django.conf import settings
from django.db.models import Q, F, Count, Sum, Subquery
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
    availability_rate = round((avail_cap / total_cap) * 100, 1) if total_cap > 0 else 0

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
        avail_pct = round((row_avail / row_total) * 100) if row_total > 0 else 0
        category_stats.append({
            'code': row['category'],
            'label': category_map.get(row['category'], row['category']),
            'count': row['count'],
            'avail': row_avail,
            'total': row_total,
            'utilized_pct': max(0, min(100, row_pct)),
            'available_pct': max(0, min(100, avail_pct)),
        })

    return {
        'totals': totals,
        'utilized_cap': utilized_cap,
        'utilization_rate': utilization_rate,
        'availability_rate': availability_rate,
        'category_stats': category_stats,
    }


def _resolve_submitter_info(resource):
    user = resource.created_by
    if not user:
        return "Verified Volunteer", ""
    profile = getattr(user, 'profile', None)
    full_name = (
        (getattr(profile, 'full_name', '') or '').strip()
        or user.get_full_name().strip()
        or user.username
    )
    organization = (getattr(profile, 'organization', '') or '').strip()
    return full_name, organization


def _serialize_resources_for_map(resources):
    map_data = []
    for r in resources:
        posted_by, posted_by_org = _resolve_submitter_info(r)
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
            'occupancy_percentage': r.occupancy_percentage,
            'confirmations': r.confirmations,
            'operating_hours': r.operating_hours,
            'contact_info': r.contact_info,
            'posted_by': posted_by,
            'posted_by_org': posted_by_org,
            'lat': r.latitude or 10.3157,
            'lng': r.longitude or 123.8854,
        })
    return map_data


def _get_user_map_config(request):
    user_settings = getattr(request.user, 'settings', None) if request.user.is_authenticated else None
    return {
        'lat': getattr(user_settings, 'default_latitude', 10.3157),
        'lng': getattr(user_settings, 'default_longitude', 123.8854),
        'zoom': getattr(user_settings, 'default_zoom', 12),
        'carto_api_key': settings.CARTO_API_KEY,
    }


def landing_view(request):
    verified_resources = Resource.objects.filter(is_verified=True)
    summary = _get_impact_summary(verified_resources)
    summary['critical_count'] = verified_resources.filter(urgency_level='CRITICAL').count()
    summary['last_updated'] = (
        verified_resources.order_by('-updated_at').values_list('updated_at', flat=True).first()
    )
    featured = (
        verified_resources.filter(category='SHELTER', status='OPERATIONAL').order_by('-confirmations', '-capacity_available').first()
        or verified_resources.filter(status='OPERATIONAL').order_by('-confirmations', '-capacity_available').first()
        or verified_resources.order_by('-confirmations').first()
    )
    status_class_map = {
        'OPERATIONAL': 'open',
        'FULL_CAPACITY': 'full',
        'TEMPORARILY_CLOSED': 'closed',
    }
    if featured:
        feat_total = featured.capacity_total or 0
        feat_avail = featured.capacity_available or 0
        feat_pct = round((feat_avail / feat_total) * 100) if feat_total > 0 else 0
        summary['featured_hub'] = {
            'name': featured.name,
            'location': featured.location,
            'category_code': featured.category,
            'category_label': featured.get_category_display(),
            'status_display': featured.get_status_display(),
            'status_class': status_class_map.get(featured.status, 'open'),
            'capacity_available': feat_avail,
            'capacity_total': feat_total,
            'available_pct': max(0, min(100, feat_pct)),
        }
    else:
        summary['featured_hub'] = None
    return render(request, 'home/landing.html', summary)


def map_view(request):
    """Public, read-only full-viewport aid map for guests and volunteers."""
    query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()
    selected_status = request.GET.get('status', '').strip()
    selected_urgency = request.GET.get('urgency', '').strip()

    all_verified = Resource.objects.filter(is_verified=True).select_related('created_by', 'created_by__profile')
    map_data = _serialize_resources_for_map(all_verified)
    user_map_config = _get_user_map_config(request)

    initial_filters = {
        'q': query,
        'category': selected_category,
        'status': selected_status,
        'urgency': selected_urgency,
    }

    context = {
        'resources': all_verified,
        'total_count': all_verified.count(),
        'critical_count': all_verified.filter(urgency_level='CRITICAL').count(),
        'categories': Resource.CATEGORY_CHOICES,
        'statuses': Resource.STATUS_CHOICES,
        'urgencies': Resource.URGENCY_CHOICES,
        'query': query,
        'selected_category': selected_category,
        'selected_status': selected_status,
        'selected_urgency': selected_urgency,
        'map_data_json': json.dumps(map_data),
        'user_map_config_json': json.dumps(user_map_config),
        'initial_filters_json': json.dumps(initial_filters),
    }
    return render(request, 'home/map.html', context)


@login_required
def dashboard_view(request):
    query = request.GET.get('q', '').strip()
    selected_status = request.GET.get('status', '').strip()
    selected_urgency = request.GET.get('urgency', '').strip()
    local_volunteers = request.GET.get('local_volunteers', '').strip()

    if 'category' in request.GET:
        selected_category = request.GET.get('category', '').strip()
    else:
        user_pref = getattr(getattr(request.user, 'settings', None), 'preferred_category', '')
        selected_category = user_pref if user_pref and user_pref != 'ALL' else ''

    resources = Resource.objects.filter(is_verified=True).select_related('created_by', 'created_by__profile')

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

    map_data = _serialize_resources_for_map(resources)
    user_map_config = _get_user_map_config(request)

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
        'user_map_config_json': json.dumps(user_map_config),
        'resource_form': ResourceForm(),
        'total_count': resources.count(),
        'operational_count': resources.filter(status='OPERATIONAL').count(),
        'critical_count': resources.filter(urgency_level='CRITICAL').count(),
    }
    return render(request, 'home/home.html', context)


# Preserve alias if imported elsewhere
home_view = dashboard_view


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
            note=f"Initial submission ({resource.get_urgency_level_display()})",
        )
        messages.success(request, f"Resource '{resource.name}' was successfully added to AyudaMap!")
    else:
        messages.error(request, "Please correct the errors in the form.")
    return redirect('home:dashboard')


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
    return redirect('home:dashboard')


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
    return redirect('home:dashboard')


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
