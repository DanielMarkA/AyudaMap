from django.contrib import admin
from .models import Resource, ResourceStatusLog


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'urgency_level', 'capacity_available', 'confirmations', 'is_verified')
    list_filter = ('category', 'status', 'urgency_level', 'is_verified')
    search_fields = ('name', 'location', 'supplies_needed')


@admin.register(ResourceStatusLog)
class ResourceStatusLogAdmin(admin.ModelAdmin):
    list_display = ('resource', 'action_type', 'new_status', 'updated_by', 'created_at')
    list_filter = ('action_type',)