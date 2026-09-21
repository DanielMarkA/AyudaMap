from django.contrib import admin
from .models import UserSettings

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'dark_mode', 'email_notifications', 'notify_on_new_resources', 'preferred_category', 'updated_at')
    list_filter = ('dark_mode', 'email_notifications', 'preferred_category')
