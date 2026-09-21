from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'organization', 'is_volunteer', 'phone_number', 'city', 'created_at')
    list_filter = ('is_volunteer', 'city')
    search_fields = ('user__username', 'full_name', 'city', 'organization')
    list_editable = ('is_volunteer',)
