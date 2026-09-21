from django.contrib import admin
from .models import Resource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'location', 'created_by', 'is_verified', 'created_at')
    list_filter = ('category', 'status', 'is_verified', 'created_at')
    search_fields = ('name', 'location', 'description', 'contact_info')
    list_editable = ('status', 'is_verified')
    autocomplete_fields = ('created_by',)
