from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    dark_mode = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    notify_on_new_resources = models.BooleanField(default=True)
    preferred_category = models.CharField(
        max_length=50,
        blank=True,
        default='ALL',
        choices=[
            ('ALL', 'All Resources'),
            ('MEDICAL', 'Medical Facilities'),
            ('FOOD', 'Food Assistance Center'),
            ('SHELTER', 'Shelter / Evacuation'),
            ('GOV', 'Government Service'),
            ('DONATION', 'Donation Center'),
        ]
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.user.username}"


@receiver(post_save, sender=User)
def create_or_update_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.get_or_create(user=instance)
    else:
        if hasattr(instance, 'settings'):
            instance.settings.save()
