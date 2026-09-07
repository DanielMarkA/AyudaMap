from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Resource

@login_required
def home_view(request):
    query = request.GET.get('q', '')
    selected_category = request.GET.get('category', '')

    resources = Resource.objects.filter(is_verified=True)

    if query:
        resources = resources.filter(name__icontains=query)
    if selected_category:
        resources = resources.filter(category=selected_category)

    context = {
        'resources': resources,
        'query': query,
        'selected_category': selected_category,
        'categories': Resource.CATEGORY_CHOICES,
    }
    return render(request, 'home/home.html', context)