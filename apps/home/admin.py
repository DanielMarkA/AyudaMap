from django.contrib import admin
from .models import Resource, ResourceStatusLog


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'category', 'status', 'is_24_7', 'opens_at', 'closes_at', 'confirmations', 'is_verified')
    list_filter = ('city', 'category', 'status', 'is_24_7', 'is_verified')
    search_fields = ('name', 'city', 'location', 'supplies_needed')


@admin.register(ResourceStatusLog)
class ResourceStatusLogAdmin(admin.ModelAdmin):
    list_display = ('resource', 'action_type', 'new_status', 'updated_by', 'created_at')
    list_filter = ('action_type',)
