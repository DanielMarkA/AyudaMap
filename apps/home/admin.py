from django.contrib import admin
from .models import Resource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'location', 'operating_hours', 'contact_info', 'is_verified', 'created_at')
    list_filter = ('category', 'is_verified')
    search_fields = ('name', 'location', 'description')
